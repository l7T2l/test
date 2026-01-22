// ═══════════════════════════════════════════════════════════════════════════════
// MediaFilter.cs - فلتر مفاتيح الوسائط
// المقابل لـ: media_filter.py (142 سطر)
// تحويل سطر بسطر - P/Invoke wrapper for media_filter.dll
// ═══════════════════════════════════════════════════════════════════════════════
// MEDIA FILTER - C# Wrapper
// =============================
// C# wrapper for media_filter.dll
// Loads the DLL and provides C# interface
// ═══════════════════════════════════════════════════════════════════════════════

using System;
using System.IO;
using System.Runtime.InteropServices;

namespace SmartKeyboard
{
    // السطر 13: Callback function type - KEYCALLBACK = ctypes.CFUNCTYPE(None, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD)
    [UnmanagedFunctionPointer(CallingConvention.Cdecl)]
    public delegate void KeyCallback(uint vkCode, uint scanCode, uint flags);

    /// <summary>
    /// class MediaFilter: - السطر 15
    /// Python wrapper for media_filter.dll
    /// </summary>
    public class MediaFilter : IDisposable
    {
        // ═══════════════════════════════════════════════════════════════
        // P/Invoke declarations for media_filter.dll
        // السطور 36-43: Function signatures
        // ═══════════════════════════════════════════════════════════════

        // Dynamic loading
        private IntPtr _dllHandle = IntPtr.Zero;

        // Function delegates
        private delegate bool StartHookDelegate();
        private delegate void StopHookDelegate();
        private delegate void SetCallbackDelegate(KeyCallback callback);
        private delegate void EnableFilterDelegate(bool enabled);
        private delegate bool IsFilterEnabledDelegate();
        private delegate bool CheckCtrlVDelegate();

        // Function pointers
        private StartHookDelegate? _startHook;
        private StopHookDelegate? _stopHook;
        private SetCallbackDelegate? _setCallback;
        private EnableFilterDelegate? _enableFilter;
        private IsFilterEnabledDelegate? _isFilterEnabled;
        private CheckCtrlVDelegate? _checkCtrlV;

        // ═══════════════════════════════════════════════════════════════
        // المتغيرات - السطور 18-21
        // ═══════════════════════════════════════════════════════════════

        // السطر 19: self.dll = None
        private bool _dllLoaded = false;

        // السطور 20-21: self.callback = None, self._py_callback = None
        private KeyCallback? _callback;
        private KeyCallback? _keepAliveCallback;

        // ═══════════════════════════════════════════════════════════════
        // LoadLibrary/GetProcAddress for dynamic DLL loading
        // ═══════════════════════════════════════════════════════════════
        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern IntPtr LoadLibrary(string dllToLoad);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern IntPtr GetProcAddress(IntPtr hModule, string procedureName);

        [DllImport("kernel32.dll", SetLastError = true)]
        private static extern bool FreeLibrary(IntPtr hModule);

        // ═══════════════════════════════════════════════════════════════
        // المُنشئ - السطر 18: def __init__(self)
        // ═══════════════════════════════════════════════════════════════
        public MediaFilter()
        {
            // السطور 19-21: Initialize to null
            _dllLoaded = false;
            _callback = null;
            _keepAliveCallback = null;
        }

        // ═══════════════════════════════════════════════════════════════
        // load - السطور 23-46
        // Load the DLL
        // ═══════════════════════════════════════════════════════════════
        public bool Load(string? dllPath = null)
        {
            // السطور 25-28: Look for DLL in same directory
            if (dllPath == null)
            {
                string scriptDir = AppDomain.CurrentDomain.BaseDirectory;
                dllPath = Path.Combine(scriptDir, "media_filter.dll");
            }

            // السطور 30-31: Check if exists
            if (!File.Exists(dllPath))
            {
                throw new FileNotFoundException($"media_filter.dll not found at: {dllPath}");
            }

            // السطر 33: Load DLL
            _dllHandle = LoadLibrary(dllPath);
            if (_dllHandle == IntPtr.Zero)
            {
                throw new Exception($"Failed to load media_filter.dll from: {dllPath}");
            }

            // السطور 36-43: Set up function pointers
            IntPtr startHookPtr = GetProcAddress(_dllHandle, "StartHook");
            IntPtr stopHookPtr = GetProcAddress(_dllHandle, "StopHook");
            IntPtr setCallbackPtr = GetProcAddress(_dllHandle, "SetCallback");
            IntPtr enableFilterPtr = GetProcAddress(_dllHandle, "EnableFilter");
            IntPtr isFilterEnabledPtr = GetProcAddress(_dllHandle, "IsFilterEnabled");
            IntPtr checkCtrlVPtr = GetProcAddress(_dllHandle, "CheckCtrlV");

            _startHook = Marshal.GetDelegateForFunctionPointer<StartHookDelegate>(startHookPtr);
            _stopHook = Marshal.GetDelegateForFunctionPointer<StopHookDelegate>(stopHookPtr);
            _setCallback = Marshal.GetDelegateForFunctionPointer<SetCallbackDelegate>(setCallbackPtr);
            _enableFilter = Marshal.GetDelegateForFunctionPointer<EnableFilterDelegate>(enableFilterPtr);
            _isFilterEnabled = Marshal.GetDelegateForFunctionPointer<IsFilterEnabledDelegate>(isFilterEnabledPtr);
            _checkCtrlV = Marshal.GetDelegateForFunctionPointer<CheckCtrlVDelegate>(checkCtrlVPtr);

            _dllLoaded = true;

            // السطر 45
            Console.WriteLine("[MEDIA-FILTER] DLL loaded");
            return true;
        }

        // ═══════════════════════════════════════════════════════════════
        // set_callback - السطور 48-55
        // Set callback function for when typing keys are blocked.
        // Callback signature: callback(vk_code, scan_code, flags)
        // ═══════════════════════════════════════════════════════════════
        public void SetCallback(KeyCallback callback)
        {
            // السطور 53-55
            _callback = callback;
            _keepAliveCallback = callback; // Keep reference to prevent GC
            _setCallback?.Invoke(callback);
        }

        // ═══════════════════════════════════════════════════════════════
        // start - السطور 57-64
        // Start the low-level keyboard hook
        // ═══════════════════════════════════════════════════════════════
        public bool Start()
        {
            if (_startHook == null) return false;

            // السطور 59-64
            if (_startHook())
            {
                Console.WriteLine("[MEDIA-FILTER] Hook started");
                return true;
            }
            else
            {
                Console.WriteLine("[MEDIA-FILTER] Failed to start hook");
                return false;
            }
        }

        // ═══════════════════════════════════════════════════════════════
        // stop - السطور 66-69
        // Stop the hook
        // ═══════════════════════════════════════════════════════════════
        public void Stop()
        {
            // السطور 68-69
            _stopHook?.Invoke();
            Console.WriteLine("[MEDIA-FILTER] Hook stopped");
        }

        // ═══════════════════════════════════════════════════════════════
        // enable - السطور 71-75
        // Enable or disable filtering
        // ═══════════════════════════════════════════════════════════════
        public void Enable(bool enabled = true)
        {
            // السطور 73-75
            _enableFilter?.Invoke(enabled);
            string state = enabled ? "enabled" : "disabled";
            Console.WriteLine($"[MEDIA-FILTER] Filter {state}");
        }

        // ═══════════════════════════════════════════════════════════════
        // is_enabled - السطور 77-79
        // Check if filter is enabled
        // ═══════════════════════════════════════════════════════════════
        public bool IsEnabled()
        {
            // السطر 79
            return _isFilterEnabled?.Invoke() ?? false;
        }

        // ═══════════════════════════════════════════════════════════════
        // check_ctrl_v - السطور 81-83
        // Check and clear Ctrl+V flag (polling)
        // ═══════════════════════════════════════════════════════════════
        public bool CheckCtrlV()
        {
            // السطر 83
            return _checkCtrlV?.Invoke() ?? false;
        }

        // ═══════════════════════════════════════════════════════════════
        // Dispose - لتحرير الموارد
        // ═══════════════════════════════════════════════════════════════
        public void Dispose()
        {
            Stop();
            if (_dllHandle != IntPtr.Zero)
            {
                FreeLibrary(_dllHandle);
                _dllHandle = IntPtr.Zero;
            }
            GC.SuppressFinalize(this);
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════════
    // Singleton instance - السطور 86-94
    // ═══════════════════════════════════════════════════════════════════════════════

    /// <summary>
    /// get_filter() - السطور 89-94
    /// Get the global MediaFilter instance
    /// </summary>
    public static class MediaFilterSingleton
    {
        // السطر 87: _filter = None
        private static MediaFilter? _filter = null;
        private static readonly object _lock = new object();

        // السطور 89-94: def get_filter()
        public static MediaFilter GetFilter()
        {
            if (_filter == null)
            {
                lock (_lock)
                {
                    if (_filter == null)
                    {
                        _filter = new MediaFilter();
                    }
                }
            }
            return _filter;
        }
    }
}
