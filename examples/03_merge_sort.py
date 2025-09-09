from jotvm import ExtJsonPatch
from jotvm.debug import SimpleDebugPrinter
import json


debug_printer = SimpleDebugPrinter()
debug_printer.enable()
# Or: debug_printer.enable() for tracing the
# computations on standard output


json_doc = {
    # get-array-slice(arr, start-idx, stop-idx)
    #   get a slice from /inp/start-idx
    #   to (including) /inp/stop-idx of the
    #   full array given at /inp/arr
    "get-array-slice": [
        # Create an empty array at /out that will
        # hold the slice eventually
        {
            "op": "add",
            "path": "/out",
            "value": [],
        },
        # Prepare array representation of JSON pointer
        # referring to current array element.
        # The last part "0" in the array will be updated
        # dynamically in the loop.
        {
            "op": "add",
            "path": "/arr-idx-ptr",
            "value": ["inp", "arr", 0]
        },
        # Prepare copy operation to copy array element
        # to the end of the array at /out. The "from" field
        # will be updated dynamically.
        {
            "op": "add",
            "path": "/copy-op",
            "value": {
                "op": "copy",
                "from": "dummy",
                "path": "/out/-",
            },
        },
        # Use a loop to copy all elements of the specified slice
        # to /out
        {
            "op": "ctrl/for-loop",
            "path": "",
            "start-value-path": "/inp/start-idx",
            "stop-value-path": "/inp/stop-idx",
            "counter-path": "/arr-idx-ptr/2",
            "patch": [
                # Upate the JSON pointer referencing
                # current array element
                {
                    "op": "array/join-path",
                    "path": "/copy-op/from",
                    "value-path": "/arr-idx-ptr"
                },
                # Apply /copy-op operation to copy this element
                # to the end of the /out array
                {
                    "op": "ctrl/apply-patch-op",
                    "patch-op-path": "/copy-op",
                    "path": "",
                },
            ],  # end of for-loop patch
        },  # end of for-lop op
        # Mission accomplished: The slice is now stored under /out
    ],

    # merge-sorted-arrays(arr1, arr2)
    #   Merges two sorted arrays at /inp/arr1
    #   and /inp/arr2 into one sorted list
    "merge-sorted-arrays": [
        # initialize an empty result array
        {
            "op": "add",
            "path": "/out",
            "value": [],
        },
        # create op that moves first value from /inp/arr1
        # to end of result array /out (appending the value)
        {
            "op": "add",
            "path": "/move-arr1-op",
            "value": {
                "op": "move",
                "from": "/inp/arr1/0",
                "path": "/out/-",
            },
        },
        # create op that moves first value from /inp/arr2
        # to end of result array /out (appending the value)
        {
            "op": "add",
            "path": "/move-arr2-op",
            "value": {
                "op": "move",
                "from": "/inp/arr2/0",
                "path": "/out/-",
            },
        },
        # create op that moves the smaller element of the
        # first arrays elements (depending on bool value at /cmp)
        # to end of result array (append)
        {
            "op": "add",
            "path": "/basic-cond-move-op",
            "value": {
                "op": "ctrl/cond-apply-patch-op",
                "path": "",
                "check": "dummy",  # dynamically changed to bool
                "true-patch-op-path": "/move-arr1-op",
                "false-patch-op-path": "/move-arr2-op",
            },
        },
        # define op that compare the first value of arr1
        # with first value of arr2
        {
            "op": "add",
            "path": "/compare-op",
            "value": {
                "op": "number/less-equal",
                "path": "/basic-cond-move-op/check",
                "left-value-path": "/inp/arr1/0",
                "right-value-path": "/inp/arr2/0",
            },
        },
        # Combine the comparison op and the
        # conditional move op to a single operation
        {
            "op": "add",
            "path": "/cond-move-op",
            "value": {
                "op": "ctrl/apply-patch",
                "path": "",
                "patch": [
                    {
                        "op": "ctrl/apply-patch-op",
                        "path": "",
                        "patch-op-path": "/compare-op",
                    },
                    {
                        "op": "ctrl/apply-patch-op",
                        "path": "",
                        "patch-op-path": "/basic-cond-move-op",
                    },
                ],
            },
        },
        # we further define an op that informs whether some
        # elements are still available for consumption in the arrays
        {
            "op": "add",
            "path": "/more-elements-available-patch",
            "value": [
                {
                    "op": "array/length",
                    "path": "/arr1-len",
                    "value-path": "/inp/arr1",
                },
                {
                    "op": "array/length",
                    "path": "/arr2-len",
                    "value-path": "/inp/arr2",
                },
                {
                    "op": "number/greater",
                    "path": "/arr1-non-empty",
                    "left-value-path": "/arr1-len",
                    "right-value": 0,
                },
                {
                    "op": "number/greater",
                    "path": "/arr2-non-empty",
                    "left-value-path": "/arr2-len",
                    "right-value": 0,
                },
                {
                    "op": "copy",
                    "from": "/arr1-non-empty",
                    "path": "/more-elements-available",
                },
                {
                    "op": "bool/or",
                    "path": "/more-elements-available",
                    "value-path": "/arr2-non-empty",
                },
            ],
        },
        # We define a variable /cur-move-op which is depending
        # on case (arr1 or arr2 exhausted) storing one of the
        # three move operations defined aboe
        {
            "op": "copy",
            "from": "/cond-move-op",
            "path": "/cur-move-op",
        },
        # Populate the /more-elements-available,
        # /arr1-non-empty and /arr2-non-empty boolean flags
        {
            "op": "ctrl/apply-patch",
            "patch-path": "/more-elements-available-patch",
            "path": "",
        },
        # Finally, we apply a while loop to merge the two arrays
        {
            "op": "ctrl/while-loop",
            "path": "",
            "check-path": "/more-elements-available",
            "patch": [
                # This instruction changes /cur-move-op
                # to the /move-arr2-op if /inp/arr1 exhausted.
                # We know this instruction will only be executed
                # if some elements in either /inp/arr1 or /inp/arr2 available
                {
                    "op": "ctrl/cond-apply-patch-op",
                    "path": "",
                    "check-path": "/arr1-non-empty",
                    "false-patch-op": {
                        "op": "copy",
                        "from": "/move-arr2-op",
                        "path": "/cur-move-op",
                    },
                },
                # This instruction changes /cur-move-op
                # to the /move-arr1-op if /inp/arr2 exhausted.
                # We know this instruction will only be executed
                # if some elements in either /inp/arr1 or /inp/arr2 available
                {
                    "op": "ctrl/cond-apply-patch-op",
                    "path": "",
                    "check-path": "/arr2-non-empty",
                    "false-patch-op": {
                        "op": "copy",
                        "from": "/move-arr1-op",
                        "path": "/cur-move-op",
                    },
                },
                # We apply the current move operation to move
                # the appropriate element to the result arr at /out
                {
                    "op": "ctrl/apply-patch-op",
                    "path": "",
                    "patch-op-path": "/cur-move-op",
                },
                # At the end of the loop, we update the boolean flags
                # indicating existence of remaining array elements
                {
                    "op": "ctrl/apply-patch",
                    "patch-path": "/more-elements-available-patch",
                    "path": "",
                },
            ],  # End of while patch
        }  # End of While Loop
        # Mission accomplished: /out contains the sorted list
    ],

    # Merge Sort algorithm
    # Expects input array at /inp/arr and sorts
    # it in ascending order. It makes use of the
    # get-array-slice and merge-sorted-arrays functions
    # defined above as well as itself. Therefore it expects
    # these functions to be available at:
    # /req/merge-sorted-arrays
    # /req/get-array-slice
    # /req/merge-sort
    # NOTE: This function expects arr to have at least two elements.
    "merge-sort": [
        # Get the largest available index (array length - 1)
        {
            "op": "array/length",
            "path": "/max-idx",
            "value-path": "/inp/arr",
        },
        {
            "op": "number/sub",
            "path": "/max-idx",
            "value": 1,
        },
        # Determine index that splits array in half
        {
            "op": "copy",
            "from": "/max-idx",
            "path": "/mid-idx",
        },
        {
            "op": "number/div",
            "path": "/mid-idx",
            "value": 2,
        },
        {
            "op": "number/trunc",
            "path": "/mid-idx",
        },
        # Obtain the lower slice and the upper slice
        {
            "op": "ctrl/call-func",
            "patch-path": "/req/get-array-slice",
            "arr-path": "/inp/arr",
            "start-idx": 0,
            "stop-idx-path": "/mid-idx",
            "out-path": "/left-slice",
        },
        {
            "op": "number/add",
            "path": "/mid-idx",
            "value": 1,
        },
        {
            "op": "ctrl/call-func",
            "patch-path": "/req/get-array-slice",
            "arr-path": "/inp/arr",
            "start-idx-path": "/mid-idx",
            "stop-idx-path": "/max-idx",
            "out-path": "/right-slice",
        },
        # If the left slice has more than one element,
        # apply merge-sort on it. If only one element,
        # do nothing as it is already sorted.
        {
            "op": "array/length",
            "path": "/left-slice-len",
            "value-path": "/left-slice",
        },
        {
            "op": "number/greater",
            "path": "/left-slice-at-least-two",
            "left-value-path": "/left-slice-len",
            "right-value": 1
        },
        {
            "op": "ctrl/cond-apply-patch-op",
            "path": "",
            "check-path": "/left-slice-at-least-two",
            "true-patch-op": {
                "op": "ctrl/call-func",
                "patch-path": "/req/merge-sort",
                "req-path": "/req",
                "arr-path": "/left-slice",
                "out-path": "/left-slice",
            },
        },
        # If the right slice has more than one element,
        # apply merge-sort on it. If only one element,
        # do nothing as it is already sorted.
        {
            "op": "array/length",
            "path": "/right-slice-len",
            "value-path": "/right-slice",
        },
        {
            "op": "number/greater",
            "path": "/right-slice-at-least-two",
            "left-value-path": "/right-slice-len",
            "right-value": 1
        },
        {
            "op": "ctrl/cond-apply-patch-op",
            "path": "",
            "check-path": "/right-slice-at-least-two",
            "true-patch-op": {
                "op": "ctrl/call-func",
                "patch-path": "/req/merge-sort",
                "req-path": "/req",
                "arr-path": "/right-slice",
                "out-path": "/right-slice",
            },
        },
        # Now we know that the two arrays stored at
        # /left-slice and /right-slice are sorted
        # and we can call /req/merge-sorted-arrays
        # to obtain one combined and sorted array.
        {
            "op": "ctrl/call-func",
            "patch-path": "/req/merge-sorted-arrays",
            "arr1-path": "/left-slice",
            "arr2-path": "/right-slice",
            "out-path": "/out",
        },
        # Mission accomplished, the sorted array is under /out
    ],

    # Some real data
    "orig-array-1": [1, 5, 10],
    "orig-array-2": [3, 7, 11],
}


patch_ops = [
    # Test the merging of two sorted array to obtain a combined sorted array
    {
        "op": "ctrl/call-func",
        "patch-path": "/merge-sorted-arrays",
        "arr1-path": "/orig-array-1",
        "arr2-path": "/orig-array-2",
        "out-path": "/combined-array-sorted",
    },
    # Test the merging of two sorted array - Variation 2
    {
        "op": "ctrl/call-func",
        "patch-path": "/merge-sorted-arrays",
        "arr1": [],
        "arr2": [3, 7, 11],
        "out-path": "/combined-array-sorted-1",
    },
    # Test the merging of two sorted array - Variation 2
    {
        "op": "ctrl/call-func",
        "patch-path": "/merge-sorted-arrays",
        "arr1": [1, 5, 10],
        "arr2": [],
        "out-path": "/combined-array-sorted-2",
    },
    # Test getting a slice of an array
    {
        "op": "ctrl/call-func",
        "patch-path": "/get-array-slice",
        "arr": [1, 2, 5, 4, 3, 6, 7],
        "start-idx": 2,
        "stop-idx": 4,
        "out-path": "/array-slice"
    },
    # Test the merge-sort algorithm to sort an array
    {
        "op": "ctrl/call-func",
        "patch-path": "/merge-sort",
        "req": {
            "merge-sort-path": "/merge-sort",
            "merge-sorted-arrays-path": "/merge-sorted-arrays",
            "get-array-slice-path": "/get-array-slice",
        },
        "arr": [3, 2, 8, 1, 4, 7, 5, 9, 6],
        "out-path": "/merge-sorted-array",
    },
]


ext_patch = ExtJsonPatch.from_list(patch_ops, debug=True)
ext_patch.apply(json_doc)

print("/orig-array-1:" + str(json_doc["orig-array-1"]))
print("/orig-array-2:" + str(json_doc["orig-array-2"]))

print("/combined-array-sorted: " + str(json_doc["combined-array-sorted"]))
print("/combined-array-sorted-1: " + str(json_doc["combined-array-sorted-1"]))
print("/combined-array-sorted-2: " + str(json_doc["combined-array-sorted-2"]))
print("/array-slice: " + str(json_doc["array-slice"]))
print("/merge-sorted-array: " + str(json_doc["merge-sorted-array"]))
