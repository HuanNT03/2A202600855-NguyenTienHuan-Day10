from __future__ import annotations

import sys
from types import ModuleType

# Shim sqlite3
try:
    import pysqlite3
    sys.modules["sqlite3"] = pysqlite3
except ImportError:
    pass

# Shim lzma
try:
    import lzma
except ImportError:
    lzma_mock = ModuleType("_lzma")
    lzma_mock.FORMAT_AUTO = 0
    lzma_mock.FORMAT_XZ = 1
    lzma_mock.FORMAT_ALONE = 2
    lzma_mock.FORMAT_RAW = 3
    lzma_mock.CHECK_NONE = 0
    lzma_mock.CHECK_CRC32 = 1
    lzma_mock.CHECK_CRC64 = 4
    lzma_mock.CHECK_SHA256 = 10
    lzma_mock.is_check_supported = lambda check: True
    lzma_mock.LZMAError = Exception
    
    class MockCompressor:
        def __init__(self, *args, **kwargs): pass
        def compress(self, data): return b''
        def flush(self): return b''
        
    class MockDecompressor:
        def __init__(self, *args, **kwargs): pass
        def decompress(self, data): return b''
        @property
        def eof(self): return True
        @property
        def unused_data(self): return b''
        
    lzma_mock.LZMACompressor = MockCompressor
    lzma_mock.LZMADecompressor = MockDecompressor
    lzma_mock._encode_filter_properties = lambda *args, **kwargs: b''
    lzma_mock._decode_filter_properties = lambda *args, **kwargs: []
    sys.modules["_lzma"] = lzma_mock

from pipelines.phase1 import main


if __name__ == "__main__":
    main()

