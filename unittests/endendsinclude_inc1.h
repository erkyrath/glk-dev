
Include "endendsinclude_inc2";

[ func37;
	return 37;
];

End;

! This constant is after the End directive, so it doesn't happen.
Constant NeverGetsDefined 1;

Everything after the End directive is ignored, so this freeform text
will not cause any problem.
