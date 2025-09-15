from jotvm import ExtJsonPatch
from jotvm.debug import SimpleDebugPrinter
from jotvm.json.types import JsonFactory


debug_printer = SimpleDebugPrinter()
debug_printer.disable()
# Or: debug_printer.enable() for tracing the
# computations on standard output


json_doc = {

    # Data that is actually code

    # scale-number(x, fact) - scales number by a factor
    'scale-number': [
        { "op": "number/mul", "path": "/inp/x", "value-path": "/inp/fact"},
        { "op": "move", "from": "/inp/x", "path": "/out"},
    ],

    # square-number(x) - square number
    'square-number': [
        { "op": "number/mul", "path": "/inp/x", "value-path": "/inp/x"},
        { "op": "move", "from": "/inp/x", "path": "/out"},
    ],

    # apply-func(arr, func, **extra-args) - apply a function to each array element 
    'map-func': [
        # Move arguments specific to apply-func out of /inp
        { "op": "move", "from": "/inp/arr", "path": "/arr" },
        { "op": "move", "from": "/inp/func", "path": "/func" },
        # Move the reduced /inp to /func-call-op to start call op preparation
        { "op": "move", "from": "/inp", "path": "/func-call-op" },  
        # Introduce all the required fields for a call-func op as well
        { "op": "add", "path": "/func-call-op/op", "value": "ctrl/call-func" },
        { "op": "add", "path": "/func-call-op/patch-path", "value": "/func" },
        { "op": "add", "path": "/func-call-op/out-path", "value": "/out/-" },
        # NOTE: "dummy" string will be replaced dynamically
        { "op": "add", "path": "/func-call-op/x-path", "value": "dummy" },
        # Determine upper limit for loop over array (array length - 1) 
        { "op": "array/length", "path": "/n", "value-path": "/arr" },
        { "op": "number/add", "path": "/n", "value": -1 },
        # Introduce an array representation of a JSON pointer into the array.
        # The last element 0 will be updated dynamically during the loop. 
        { "op": "add", "path": "/idx", "value": ["arr", 0] }, 
        # Initialize the output array
        { "op": "add", "path": "/out", "value": [] },
        # Run the loop to apply func to each array element
        {
            "op": "ctrl/for-loop",
            "path": "",
            "counter-path": "/idx/1",  # This injects the counter value at 
            "start-value": 0,          # the zero position above.
            "stop-value-path": "/n",
            "patch": [
                # Convert the array representation to a JSON pointer string
                { "op": "array/join-path", "path": "/idx-ptr", "value-path": "/idx" },
                # Inject this JSON Pointer into the /func-call-op defined above 
                { "op": "copy", "from": "/idx-ptr", "path": "/func-call-op/x-path" },
                # Call the function to update the current array element 
                { "op": "ctrl/apply-patch-op", "path": "",  "patch-op-path": "/func-call-op" },
            ]
        },
    ],

    # Here some data
    "orig-arr": [1, 2, 3],
}


patch_ops = [
    # Test the scale-number function
    {
        "op": "ctrl/call-func",
        "patch-path": "/scale-number",
        "x": 10, "fact": 3,
        "out-path": "/scaled-value"
    },
    # Test the square-number function
    {
        "op": "ctrl/call-func",
        "patch-path": "/square-number",
        "x": 12,
        "out-path": "/squared-value",
    },
    # Test the map-func array function with scale-number
    {
        "op": "ctrl/call-func",
        "patch-path": "/map-func",
        "func-path": "/scale-number",
        "arr-path": "/orig-arr",
        "fact": 5,
        "out-path": "/scaled-arr",
    },
    # Test the map-func array function with square-number
    {
        "op": "ctrl/call-func",
        "patch-path": "/map-func",
        "func-path": "/square-number",
        "arr-path": "/orig-arr",
        "fact": 5,
        "out-path": "/squared-arr",
    },
]


json_doc = JsonFactory.from_python(json_doc, require_decimal=False)
ext_patch = ExtJsonPatch.from_python(patch_ops, require_decimal=False)
ext_patch.apply(json_doc)

print(f"Original array: {json_doc['orig-arr'].to_python()}")
print(f"Scaled array: {json_doc['scaled-arr'].to_python()}")
print(f"Squared array: {json_doc['squared-arr'].to_python()}")
