const problems = [
  {
    title: "Two Sum",
    description:
      "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.\n(For non-Python: input format -> first line n, second line nums, third line target. Output -> two indices.)",
    starters: {
      python:
        "def solve(arr, t):\n" +
        "    # Write your solution here\n" +
        "    pass\n"
    },
    public_tests: [
      { call: "solve([2,7,11,15], 9)", output: [0, 1] },
      { call: "solve([3,2,4], 6)", output: [1, 2] },
      { call: "solve([1,5,3,7], 8)", output: [0, 3] }
    ],
    hidden_tests: [
      { call: "solve([1,2,3,4], 5)", output: [0, 3] },
      { call: "solve([10,20,10,40,50,70], 50)", output: [0, 3] },
      { call: "solve([5,75,25], 100)", output: [1, 2] },
      { call: "solve([2,5,5,11], 10)", output: [1, 2] },
      { call: "solve([0,4,3,0], 0)", output: [0, 3] },
      { call: "solve([-3,4,3,90], 0)", output: [0, 2] },
      { call: "solve([1,3,4,2], 6)", output: [1, 3] },
      { call: "solve([1,2], 3)", output: [0, 1] },
      { call: "solve([2,4,3], 6)", output: [0, 2] },
      { call: "solve([3,3], 6)", output: [0, 1] },
      { call: "solve([8,7,2,1], 9)", output: [1, 3] },
      { call: "solve([4,4,1,2], 8)", output: [0, 1] },
      { call: "solve([1,9], 10)", output: [0, 1] },
      { call: "solve([6,1,3,4,2], 5)", output: [3, 4] },
      { call: "solve([-1,-2,-3,-4,-5], -8)", output: [2, 3] }
    ]
  },

  {
    title: "Valid Parentheses",
    description:
      "Given a string containing ()[]{} return true/false.\n(Non-Python: input is the string; output true or false lowercase.)",
    starters: {
      python:
        "def solve(s):\n" +
        "    # Write your solution here\n" +
        "    pass\n"
    },
    public_tests: [
      { call: "solve('()')", output: true },
      { call: "solve('()[]{}')", output: true },
      { call: "solve('(]')", output: false }
    ],
    hidden_tests: [
      { call: "solve('([)]')", output: false },
      { call: "solve('{[]}')", output: true },
      { call: "solve('')", output: true },
      { call: "solve('(')", output: false },
      { call: "solve(']')", output: false },
      { call: "solve('(([]){})')", output: true },
      { call: "solve('([{}])')", output: true },
      { call: "solve('{[}]')", output: false },
      { call: "solve('((()))')", output: true },
      { call: "solve('{')", output: false },
      { call: "solve('([)')", output: false },
      { call: "solve('[]{}()')", output: true },
      { call: "solve('([{}])(){}[]')", output: true },
      { call: "solve('([{})')", output: false }
    ]
  },

  {
    title: "Longest Common Prefix",
    description:
      "Find the longest common prefix of an array of strings.",
    starters: {
      python:
        "def solve(strs):\n" +
        "    # Write your solution here\n" +
        "    pass\n"
    },
    public_tests: [
      { call: "solve(['flower','flow','flight'])", output: "fl" },
      { call: "solve(['a'])", output: "a" },
      { call: "solve(['interview','integrate','integer'])", output: "inte" }
    ],
    hidden_tests: [
      { call: "solve(['dog','racecar','car'])", output: "" },
      { call: "solve(['c','c'])", output: "c" },
      { call: "solve(['prefix','preach','preform','pre'])", output: "pre" },
      { call: "solve([])", output: "" },
      { call: "solve(['same','same','same'])", output: "same" },
      { call: "solve(['ab','a'])", output: "a" },
      { call: "solve(['abc','abcd','abf'])", output: "ab" },
      { call: "solve(['z'])", output: "z" },
      { call: "solve(['apple','banana','carrot'])", output: "" },
      { call: "solve(['longest','long','longitudinal'])", output: "long" },
      { call: "solve(['xxy','xxyz','xxyzz'])", output: "xxy" },
      { call: "solve(['m','m','m','m'])", output: "m" },
      { call: "solve(['prefixer','prefix','pre'])", output: "pre" },
      { call: "solve(['alpha','alph','alp'])", output: "alp" },
      { call: "solve(['abca','abc','ab'])", output: "ab" }
    ]
  },

  {
    title: "Maximum Subarray",
    description:
      "Return the maximum sum of a contiguous subarray.",
    starters: {
      python:
        "def solve(nums):\n" +
        "    # Write your solution here\n" +
        "    pass\n"
    },
    public_tests: [
      { call: "solve([-2,1,-3,4,-1,2,1,-5,4])", output: 6 },
      { call: "solve([1])", output: 1 },
      { call: "solve([5,4,-1,7,8])", output: 23 }
    ],
    hidden_tests: [
      { call: "solve([-1,-2,-3,-4])", output: -1 },
      { call: "solve([0,0,0])", output: 0 },
      { call: "solve([2,-1,2,3,4,-5])", output: 10 },
      { call: "solve([1,2,3,4,5])", output: 15 },
      { call: "solve([-2,1])", output: 1 },
      { call: "solve([ -2, -1, -3, -4, 0 ])", output: 0 },
      { call: "solve([ -1, 0, -2 ])", output: 0 },
      { call: "solve([100,-1,-2,50])", output: 147 },
      { call: "solve([ -5, 4, -1, 7, 8, -20, 10 ])", output: 18 },
      { call: "solve([10,-3,1,2,-1,5])", output: 14 },
      { call: "solve([ -2 ])", output: -2 },
      { call: "solve([3,-2,5,-1])", output: 6 },
      { call: "solve([ -1, 3, -2, 5, -1 ])", output: 6 },
      { call: "solve([2,-8,3,-2,4,-10])", output: 5 },
      { call: "solve([0,-3,1,2,-1,2])", output: 4 }
    ]
  },

  {
    title: "Merge Intervals",
    description: "Merge overlapping intervals.",
    starters: {
      python:
        "def solve(intervals):\n" +
        "    # Write your solution here\n" +
        "    pass\n"
    },
    public_tests: [
      { call: "solve([[1,3],[2,6],[8,10],[15,18]])", output: [[1,6],[8,10],[15,18]] },
      { call: "solve([[1,4],[0,4]])", output: [[0,4]] },
      { call: "solve([[1,4],[4,5]])", output: [[1,5]] }
    ],
    hidden_tests: [
      { call: "solve([])", output: [] },
      { call: "solve([[1,4]])", output: [[1,4]] },
      { call: "solve([[1,3],[2,4],[5,7]])", output: [[1,4],[5,7]] },
      { call: "solve([[6,8],[1,9],[2,4],[4,7]])", output: [[1,9]] },
      { call: "solve([[1,10],[2,3],[4,5]])", output: [[1,10]] },
      { call: "solve([[2,3],[4,5],[6,7]])", output: [[2,3],[4,5],[6,7]] },
      { call: "solve([[1,4],[5,6]])", output: [[1,4],[5,6]] },
      { call: "solve([[1,4],[0,2]])", output: [[0,4]] },
      { call: "solve([[1,4],[0,1]])", output: [[0,4]] },
      { call: "solve([[1,4],[2,3]])", output: [[1,4]] },
      { call: "solve([[0,0],[0,0]])", output: [[0,0]] },
      { call: "solve([[1,5],[2,3],[4,8]])", output: [[1,8]] },
      { call: "solve([[5,6],[1,2],[2,4]])", output: [[1,4],[5,6]] },
      { call: "solve([[1,2],[2,3],[3,4]])", output: [[1,4]] },
      { call: "solve([[10,12],[1,3],[2,6],[8,10]])", output: [[1,6],[8,12]] }
    ]
  }
];
