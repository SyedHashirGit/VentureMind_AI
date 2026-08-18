import os
import sys

# Since glide-for-redis does not support Windows natively, fall back to mock stubs immediately on Windows.
# This prevents recursion loops and path resolution issues in local development.
if os.name == 'nt':
    class _PubSubChannelModes:
        Exact = "Exact"

    class _PubSubSubscriptions:
        def __init__(self, *a, **k):
            pass

    class _Dummy:
        def __init__(self, *a, **k):
            pass
        @staticmethod
        async def create(*a, **k):
            raise ImportError("glide-for-redis is not supported on Windows.")
        PubSubSubscriptions = _PubSubSubscriptions
        PubSubChannelModes = _PubSubChannelModes

    # Expose mock classes matching glide interface
    GlideClient = _Dummy
    GlideClientConfiguration = _Dummy
    NodeAddress = _Dummy

else:
    # On Linux/macOS/production, try to load the real glide-for-redis package
    dir_path = os.path.dirname(os.path.abspath(__file__))
    original_path = sys.path.copy()
    abs_paths = [os.path.abspath(p) if p else os.getcwd() for p in sys.path]
    indices_to_remove = [i for i, p in enumerate(abs_paths) if p == dir_path]
    for i in reversed(indices_to_remove):
         sys.path.pop(i)

    try:
        # Temporarily pop ourselves from sys.modules to force system lookup
        self_module = sys.modules.pop('glide', None)
        import glide as _real_glide
        
        # Expose all symbols from the real package
        globals().update({k: v for k, v in _real_glide.__dict__.items() if not k.startswith('__')})
        sys.modules['glide'] = _real_glide
    except ImportError:
        class _PubSubChannelModes:
            Exact = "Exact"

        class _PubSubSubscriptions:
            def __init__(self, *a, **k):
                pass

        class _Dummy:
            def __init__(self, *a, **k):
                pass
            @staticmethod
            async def create(*a, **k):
                raise ImportError("glide-for-redis is not installed.")
            PubSubSubscriptions = _PubSubSubscriptions
            PubSubChannelModes = _PubSubChannelModes

        GlideClient = _Dummy
        GlideClientConfiguration = _Dummy
        NodeAddress = _Dummy
    finally:
        sys.path = original_path
