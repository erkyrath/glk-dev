
!System_file;

! Will be replaced (entirely).
[ funcbeta;
    print "original funcbeta.^";
    failures++;  ! Should not be called.
    return 3;
];

! Will be replaced, but will live on as funcdeltaorig.
[ funcdelta;
    print "original funcdelta.^";
    return 4;
];

