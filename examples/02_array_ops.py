from jotvm import ExtJsonPatch
from jotvm.debug import SimpleDebugPrinter
from jotvm.json.types import JsonFactory


debug_printer = SimpleDebugPrinter()
debug_printer.enable()
# Or: debug_printer.enable() for tracing the
# computations on standard output


json_doc = {
    # Takes a JSON pointer under /inp/path
    # and appends a path element given
    # under /inp/i. Facilitates array
    # operations.
    'create-json-pointer-index': [
        # Prepare an array representation
        # of the JSON pointer passed under
        # /inp/path
        {
            "op": "string/split-path",
            "path": "/jsonptr-arr",
            "value-path": "/inp/path",
        },
        # Update this array representation
        # by appending as element the value under /inp/i.
        # The special part "-" can be used to indicate
        # as index the length of the array.
        {
            "op": "add",
            "path": "/jsonptr-arr/-",
            "value-path": "/inp/i",
        },
        # Convert the JSON pointer array representation
        # back to a string, which is stored under /out
        {
            "op": "array/join-path",
            "path": "/out",
            "value-path": "/jsonptr-arr",
        },
        # Mission accomplished, full JSON pointer
        # in string form stored under /out.
    ],

    # This function expects the array under
    # /inp/arr and the index under /inp/i
    # This function relies on the create-json-pointer-index function,
    # which must be passed under /req/create-json-pointer-index
    'get-array-element': [
        # Prepare the copy instruction to copy array element
        # to /out. The "from" field will updated with the next instruction.
        {
            "op": "add",
            "path": "/copy-op",
            "value": {
                "op": "copy",
                "from": "dummy",
                "path": "/out",
            }
        },
        # Create a JSON pointer referencing the desired array element
        # and insert it into the copy-op instruction prepared under /copy-op
        {
            "op": "ctrl/call-func",
            "patch-path": "/req/create-json-pointer-index",
            "path": "/inp/arr",
            "i-path": "/inp/i",
            "out-path": "/copy-op/from",
        },
        # Execute the copy-op instruction to copy the array element to /out
        {
            "op": "ctrl/apply-patch-op",
            "path": "",
            "patch-op-path": "/copy-op",
        }
        # Mission accomplished, the requested
        # array element is available under /out
    ],

    # This function expects the array under
    # /inp/arr, the new value under /inp/v and the index under /inp/i.
    # It is assumed that the array index already
    # exists, hence the array size is not expanded.
    # This function relies on the create-json-pointer-index function,
    # which must be passed under /req/create-json-pointer-index
    "set-array-element": [
        # Prepare the replace instruction to copy /inp/v into the array at /inp/arr
        {
            "op": "add",
            "path": "/replace-op",
            "value": {
                "op": "replace",
                "path": "dummy",
                "value-path": "/inp/v",
            }
        },
        # Create a JSON pointer referencing the desired array element
        # and insert it into the replace instruction prepared under /copy-op
        {
            "op": "ctrl/call-func",
            "patch-path": "/req/create-json-pointer-index",
            "path": "/inp/arr",
            "i-path": "/inp/i",
            "out-path": "/replace-op/path",
        },
        # Execute the replace instruction to update the desired array element
        {
            "op": "ctrl/apply-patch-op",
            "path": "",
            "patch-op-path": "/replace-op",
        },
        # Move the array to the /out
        {
            "op": "move",
            "from": "/inp/arr",
            "path": "/out",
        }
    ],

    # Some real data
    "orig-array": [10, 9, 8],
}


patch_ops = [
    # Test the get-array-element function
    {
        "op": "ctrl/call-func",
        "patch-path": "/get-array-element",
        "req": {"create-json-pointer-index-path": "/create-json-pointer-index"},
        "arr-path": "/orig-array",
        "i": 2,
        "out-path": "/picked-element",
    },
    # Test the set-array-element function
    {
        "op": "ctrl/call-func",
        "patch-path": "/set-array-element",
        "req": {"create-json-pointer-index-path": "/create-json-pointer-index"},
        "arr-path": "/orig-array",
        "i": 0,
        "v": 19,
        "out-path": "/modified-array",
    },
]


json_doc = JsonFactory.from_python(json_doc, require_decimal=False)
ext_patch = ExtJsonPatch.from_python(patch_ops, require_decimal=False)
ext_patch.apply(json_doc)

print("/orig-array: " + str(json_doc["orig-array"].to_python()))
print("/picked-element: " + str(json_doc["picked-element"].to_python()))
print("/modified-array: " + str(json_doc["modified-array"].to_python()))
