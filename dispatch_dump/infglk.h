Constant evtype_Arrange = 5;
Constant evtype_CharInput = 2;
Constant evtype_Hyperlink = 8;
Constant evtype_LineInput = 3;
Constant evtype_MouseInput = 4;
Constant evtype_None = 0;
Constant evtype_Redraw = 6;
Constant evtype_SoundNotify = 7;
Constant evtype_Timer = 1;
Constant filemode_Read = 2;
Constant filemode_ReadWrite = 3;
Constant filemode_Write = 1;
Constant filemode_WriteAppend = 5;
Constant fileusage_BinaryMode = 0;
Constant fileusage_Data = 0;
Constant fileusage_InputRecord = 3;
Constant fileusage_SavedGame = 1;
Constant fileusage_TextMode = 256;
Constant fileusage_Transcript = 2;
Constant fileusage_TypeMask = 15;
Constant gestalt_CharInput = 1;
Constant gestalt_CharOutput = 3;
Constant gestalt_CharOutput_ApproxPrint = 1;
Constant gestalt_CharOutput_CannotPrint = 0;
Constant gestalt_CharOutput_ExactPrint = 2;
Constant gestalt_DrawImage = 7;
Constant gestalt_Graphics = 6;
Constant gestalt_GraphicsTransparency = 14;
Constant gestalt_HyperlinkInput = 12;
Constant gestalt_Hyperlinks = 11;
Constant gestalt_LineInput = 2;
Constant gestalt_LineInputEcho = 17;
Constant gestalt_LineTerminatorKey = 19;
Constant gestalt_LineTerminators = 18;
Constant gestalt_MouseInput = 4;
Constant gestalt_Sound = 8;
Constant gestalt_SoundMusic = 13;
Constant gestalt_SoundNotify = 10;
Constant gestalt_SoundVolume = 9;
Constant gestalt_Timer = 5;
Constant gestalt_Unicode = 15;
Constant gestalt_UnicodeNorm = 16;
Constant gestalt_Version = 0;
Constant imagealign_InlineCenter = 3;
Constant imagealign_InlineDown = 2;
Constant imagealign_MarginLeft = 4;
Constant imagealign_MarginRight = 5;
Constant imagealign_InlineUp = 1;
Constant keycode_Delete = -7;
Constant keycode_Down = -5;
Constant keycode_End = -13;
Constant keycode_Escape = -8;
Constant keycode_Func1 = -17;
Constant keycode_Func10 = -26;
Constant keycode_Func11 = -27;
Constant keycode_Func12 = -28;
Constant keycode_Func2 = -18;
Constant keycode_Func3 = -19;
Constant keycode_Func4 = -20;
Constant keycode_Func5 = -21;
Constant keycode_Func6 = -22;
Constant keycode_Func7 = -23;
Constant keycode_Func8 = -24;
Constant keycode_Func9 = -25;
Constant keycode_Home = -12;
Constant keycode_Left = -2;
Constant keycode_MAXVAL = 28;
Constant keycode_PageDown = -11;
Constant keycode_PageUp = -10;
Constant keycode_Return = -6;
Constant keycode_Right = -3;
Constant keycode_Tab = -9;
Constant keycode_Unknown = -1;
Constant keycode_Up = -4;
Constant seekmode_Current = 1;
Constant seekmode_End = 2;
Constant seekmode_Start = 0;
Constant style_Alert = 5;
Constant style_BlockQuote = 7;
Constant style_Emphasized = 1;
Constant style_Header = 3;
Constant style_Input = 8;
Constant style_NUMSTYLES = 11;
Constant style_Normal = 0;
Constant style_Note = 6;
Constant style_Preformatted = 2;
Constant style_Subheader = 4;
Constant style_User1 = 9;
Constant style_User2 = 10;
Constant stylehint_BackColor = 8;
Constant stylehint_Indentation = 0;
Constant stylehint_Justification = 2;
Constant stylehint_NUMHINTS = 10;
Constant stylehint_Oblique = 5;
Constant stylehint_ParaIndentation = 1;
Constant stylehint_Proportional = 6;
Constant stylehint_ReverseColor = 9;
Constant stylehint_Size = 3;
Constant stylehint_TextColor = 7;
Constant stylehint_Weight = 4;
Constant stylehint_just_Centered = 2;
Constant stylehint_just_LeftFlush = 0;
Constant stylehint_just_LeftRight = 1;
Constant stylehint_just_RightFlush = 3;
Constant winmethod_Above = 2;
Constant winmethod_Below = 3;
Constant winmethod_Border = 0;
Constant winmethod_BorderMask = 256;
Constant winmethod_DirMask = 15;
Constant winmethod_DivisionMask = 240;
Constant winmethod_Fixed = 16;
Constant winmethod_Left = 0;
Constant winmethod_NoBorder = 256;
Constant winmethod_Proportional = 32;
Constant winmethod_Right = 1;
Constant wintype_AllTypes = 0;
Constant wintype_Blank = 2;
Constant wintype_Graphics = 5;
Constant wintype_Pair = 1;
Constant wintype_TextBuffer = 3;
Constant wintype_TextGrid = 4;

[ glk_exit _vararg_count;
  ! glk_exit()
  @glk 1 _vararg_count 0;
  return 0;
];

[ glk_tick _vararg_count;
  ! glk_tick()
  @glk 3 _vararg_count 0;
  return 0;
];

[ glk_gestalt _vararg_count ret;
  ! glk_gestalt(uint, uint) => uint
  @glk 4 _vararg_count ret;
  return ret;
];

[ glk_gestalt_ext _vararg_count ret;
  ! glk_gestalt_ext(uint, uint, uintarray, arraylen) => uint
  @glk 5 _vararg_count ret;
  return ret;
];

[ glk_window_iterate _vararg_count ret;
  ! glk_window_iterate(window, &uint) => window
  @glk 32 _vararg_count ret;
  return ret;
];

[ glk_window_get_rock _vararg_count ret;
  ! glk_window_get_rock(window) => uint
  @glk 33 _vararg_count ret;
  return ret;
];

[ glk_window_get_root _vararg_count ret;
  ! glk_window_get_root() => window
  @glk 34 _vararg_count ret;
  return ret;
];

[ glk_window_open _vararg_count ret;
  ! glk_window_open(window, uint, uint, uint, uint) => window
  @glk 35 _vararg_count ret;
  return ret;
];

[ glk_window_close _vararg_count;
  ! glk_window_close(window, &{uint, uint})
  @glk 36 _vararg_count 0;
  return 0;
];

[ glk_window_get_size _vararg_count;
  ! glk_window_get_size(window, &uint, &uint)
  @glk 37 _vararg_count 0;
  return 0;
];

[ glk_window_set_arrangement _vararg_count;
  ! glk_window_set_arrangement(window, uint, uint, window)
  @glk 38 _vararg_count 0;
  return 0;
];

[ glk_window_get_arrangement _vararg_count;
  ! glk_window_get_arrangement(window, &uint, &uint, &window)
  @glk 39 _vararg_count 0;
  return 0;
];

[ glk_window_get_type _vararg_count ret;
  ! glk_window_get_type(window) => uint
  @glk 40 _vararg_count ret;
  return ret;
];

[ glk_window_get_parent _vararg_count ret;
  ! glk_window_get_parent(window) => window
  @glk 41 _vararg_count ret;
  return ret;
];

[ glk_window_clear _vararg_count;
  ! glk_window_clear(window)
  @glk 42 _vararg_count 0;
  return 0;
];

[ glk_window_move_cursor _vararg_count;
  ! glk_window_move_cursor(window, uint, uint)
  @glk 43 _vararg_count 0;
  return 0;
];

[ glk_window_get_stream _vararg_count ret;
  ! glk_window_get_stream(window) => stream
  @glk 44 _vararg_count ret;
  return ret;
];

[ glk_window_set_echo_stream _vararg_count;
  ! glk_window_set_echo_stream(window, stream)
  @glk 45 _vararg_count 0;
  return 0;
];

[ glk_window_get_echo_stream _vararg_count ret;
  ! glk_window_get_echo_stream(window) => stream
  @glk 46 _vararg_count ret;
  return ret;
];

[ glk_set_window _vararg_count;
  ! glk_set_window(window)
  @glk 47 _vararg_count 0;
  return 0;
];

[ glk_window_get_sibling _vararg_count ret;
  ! glk_window_get_sibling(window) => window
  @glk 48 _vararg_count ret;
  return ret;
];

[ glk_stream_iterate _vararg_count ret;
  ! glk_stream_iterate(stream, &uint) => stream
  @glk 64 _vararg_count ret;
  return ret;
];

[ glk_stream_get_rock _vararg_count ret;
  ! glk_stream_get_rock(stream) => uint
  @glk 65 _vararg_count ret;
  return ret;
];

[ glk_stream_open_file _vararg_count ret;
  ! glk_stream_open_file(fileref, uint, uint) => stream
  @glk 66 _vararg_count ret;
  return ret;
];

[ glk_stream_open_memory _vararg_count ret;
  ! glk_stream_open_memory(nativechararray, arraylen, uint, uint) => stream
  @glk 67 _vararg_count ret;
  return ret;
];

[ glk_stream_close _vararg_count;
  ! glk_stream_close(stream, &{uint, uint})
  @glk 68 _vararg_count 0;
  return 0;
];

[ glk_stream_set_position _vararg_count;
  ! glk_stream_set_position(stream, int, uint)
  @glk 69 _vararg_count 0;
  return 0;
];

[ glk_stream_get_position _vararg_count ret;
  ! glk_stream_get_position(stream) => uint
  @glk 70 _vararg_count ret;
  return ret;
];

[ glk_stream_set_current _vararg_count;
  ! glk_stream_set_current(stream)
  @glk 71 _vararg_count 0;
  return 0;
];

[ glk_stream_get_current _vararg_count ret;
  ! glk_stream_get_current() => stream
  @glk 72 _vararg_count ret;
  return ret;
];

[ glk_fileref_create_temp _vararg_count ret;
  ! glk_fileref_create_temp(uint, uint) => fileref
  @glk 96 _vararg_count ret;
  return ret;
];

[ glk_fileref_create_by_name _vararg_count ret;
  ! glk_fileref_create_by_name(uint, string, uint) => fileref
  @glk 97 _vararg_count ret;
  return ret;
];

[ glk_fileref_create_by_prompt _vararg_count ret;
  ! glk_fileref_create_by_prompt(uint, uint, uint) => fileref
  @glk 98 _vararg_count ret;
  return ret;
];

[ glk_fileref_destroy _vararg_count;
  ! glk_fileref_destroy(fileref)
  @glk 99 _vararg_count 0;
  return 0;
];

[ glk_fileref_iterate _vararg_count ret;
  ! glk_fileref_iterate(fileref, &uint) => fileref
  @glk 100 _vararg_count ret;
  return ret;
];

[ glk_fileref_get_rock _vararg_count ret;
  ! glk_fileref_get_rock(fileref) => uint
  @glk 101 _vararg_count ret;
  return ret;
];

[ glk_fileref_delete_file _vararg_count;
  ! glk_fileref_delete_file(fileref)
  @glk 102 _vararg_count 0;
  return 0;
];

[ glk_fileref_does_file_exist _vararg_count ret;
  ! glk_fileref_does_file_exist(fileref) => uint
  @glk 103 _vararg_count ret;
  return ret;
];

[ glk_fileref_create_from_fileref _vararg_count ret;
  ! glk_fileref_create_from_fileref(uint, fileref, uint) => fileref
  @glk 104 _vararg_count ret;
  return ret;
];

[ glk_put_char _vararg_count;
  ! glk_put_char(uchar)
  @glk 128 _vararg_count 0;
  return 0;
];

[ glk_put_char_stream _vararg_count;
  ! glk_put_char_stream(stream, uchar)
  @glk 129 _vararg_count 0;
  return 0;
];

[ glk_put_string _vararg_count;
  ! glk_put_string(string)
  @glk 130 _vararg_count 0;
  return 0;
];

[ glk_put_string_stream _vararg_count;
  ! glk_put_string_stream(stream, string)
  @glk 131 _vararg_count 0;
  return 0;
];

[ glk_put_buffer _vararg_count;
  ! glk_put_buffer(nativechararray, arraylen)
  @glk 132 _vararg_count 0;
  return 0;
];

[ glk_put_buffer_stream _vararg_count;
  ! glk_put_buffer_stream(stream, nativechararray, arraylen)
  @glk 133 _vararg_count 0;
  return 0;
];

[ glk_set_style _vararg_count;
  ! glk_set_style(uint)
  @glk 134 _vararg_count 0;
  return 0;
];

[ glk_set_style_stream _vararg_count;
  ! glk_set_style_stream(stream, uint)
  @glk 135 _vararg_count 0;
  return 0;
];

[ glk_get_char_stream _vararg_count ret;
  ! glk_get_char_stream(stream) => int
  @glk 144 _vararg_count ret;
  return ret;
];

[ glk_get_line_stream _vararg_count ret;
  ! glk_get_line_stream(stream, nativechararray, arraylen) => uint
  @glk 145 _vararg_count ret;
  return ret;
];

[ glk_get_buffer_stream _vararg_count ret;
  ! glk_get_buffer_stream(stream, nativechararray, arraylen) => uint
  @glk 146 _vararg_count ret;
  return ret;
];

[ glk_char_to_lower _vararg_count ret;
  ! glk_char_to_lower(uchar) => uchar
  @glk 160 _vararg_count ret;
  return ret;
];

[ glk_char_to_upper _vararg_count ret;
  ! glk_char_to_upper(uchar) => uchar
  @glk 161 _vararg_count ret;
  return ret;
];

[ glk_stylehint_set _vararg_count;
  ! glk_stylehint_set(uint, uint, uint, int)
  @glk 176 _vararg_count 0;
  return 0;
];

[ glk_stylehint_clear _vararg_count;
  ! glk_stylehint_clear(uint, uint, uint)
  @glk 177 _vararg_count 0;
  return 0;
];

[ glk_style_distinguish _vararg_count ret;
  ! glk_style_distinguish(window, uint, uint) => uint
  @glk 178 _vararg_count ret;
  return ret;
];

[ glk_style_measure _vararg_count ret;
  ! glk_style_measure(window, uint, uint, &uint) => uint
  @glk 179 _vararg_count ret;
  return ret;
];

[ glk_select _vararg_count;
  ! glk_select(&{uint, window, uint, uint})
  @glk 192 _vararg_count 0;
  return 0;
];

[ glk_select_poll _vararg_count;
  ! glk_select_poll(&{uint, window, uint, uint})
  @glk 193 _vararg_count 0;
  return 0;
];

[ glk_request_line_event _vararg_count;
  ! glk_request_line_event(window, nativechararray, arraylen, uint)
  @glk 208 _vararg_count 0;
  return 0;
];

[ glk_cancel_line_event _vararg_count;
  ! glk_cancel_line_event(window, &{uint, window, uint, uint})
  @glk 209 _vararg_count 0;
  return 0;
];

[ glk_request_char_event _vararg_count;
  ! glk_request_char_event(window)
  @glk 210 _vararg_count 0;
  return 0;
];

[ glk_cancel_char_event _vararg_count;
  ! glk_cancel_char_event(window)
  @glk 211 _vararg_count 0;
  return 0;
];

[ glk_request_mouse_event _vararg_count;
  ! glk_request_mouse_event(window)
  @glk 212 _vararg_count 0;
  return 0;
];

[ glk_cancel_mouse_event _vararg_count;
  ! glk_cancel_mouse_event(window)
  @glk 213 _vararg_count 0;
  return 0;
];

[ glk_request_timer_events _vararg_count;
  ! glk_request_timer_events(uint)
  @glk 214 _vararg_count 0;
  return 0;
];

[ glk_image_get_info _vararg_count ret;
  ! glk_image_get_info(uint, &uint, &uint) => uint
  @glk 224 _vararg_count ret;
  return ret;
];

[ glk_image_draw _vararg_count ret;
  ! glk_image_draw(window, uint, int, int) => uint
  @glk 225 _vararg_count ret;
  return ret;
];

[ glk_image_draw_scaled _vararg_count ret;
  ! glk_image_draw_scaled(window, uint, int, int, uint, uint) => uint
  @glk 226 _vararg_count ret;
  return ret;
];

[ glk_window_flow_break _vararg_count;
  ! glk_window_flow_break(window)
  @glk 232 _vararg_count 0;
  return 0;
];

[ glk_window_erase_rect _vararg_count;
  ! glk_window_erase_rect(window, int, int, uint, uint)
  @glk 233 _vararg_count 0;
  return 0;
];

[ glk_window_fill_rect _vararg_count;
  ! glk_window_fill_rect(window, uint, int, int, uint, uint)
  @glk 234 _vararg_count 0;
  return 0;
];

[ glk_window_set_background_color _vararg_count;
  ! glk_window_set_background_color(window, uint)
  @glk 235 _vararg_count 0;
  return 0;
];

[ glk_schannel_iterate _vararg_count ret;
  ! glk_schannel_iterate(schannel, &uint) => schannel
  @glk 240 _vararg_count ret;
  return ret;
];

[ glk_schannel_get_rock _vararg_count ret;
  ! glk_schannel_get_rock(schannel) => uint
  @glk 241 _vararg_count ret;
  return ret;
];

[ glk_schannel_create _vararg_count ret;
  ! glk_schannel_create(uint) => schannel
  @glk 242 _vararg_count ret;
  return ret;
];

[ glk_schannel_destroy _vararg_count;
  ! glk_schannel_destroy(schannel)
  @glk 243 _vararg_count 0;
  return 0;
];

[ glk_schannel_play _vararg_count ret;
  ! glk_schannel_play(schannel, uint) => uint
  @glk 248 _vararg_count ret;
  return ret;
];

[ glk_schannel_play_ext _vararg_count ret;
  ! glk_schannel_play_ext(schannel, uint, uint, uint) => uint
  @glk 249 _vararg_count ret;
  return ret;
];

[ glk_schannel_stop _vararg_count;
  ! glk_schannel_stop(schannel)
  @glk 250 _vararg_count 0;
  return 0;
];

[ glk_schannel_set_volume _vararg_count;
  ! glk_schannel_set_volume(schannel, uint)
  @glk 251 _vararg_count 0;
  return 0;
];

[ glk_sound_load_hint _vararg_count;
  ! glk_sound_load_hint(uint, uint)
  @glk 252 _vararg_count 0;
  return 0;
];

[ glk_set_hyperlink _vararg_count;
  ! glk_set_hyperlink(uint)
  @glk 256 _vararg_count 0;
  return 0;
];

[ glk_set_hyperlink_stream _vararg_count;
  ! glk_set_hyperlink_stream(stream, uint)
  @glk 257 _vararg_count 0;
  return 0;
];

[ glk_request_hyperlink_event _vararg_count;
  ! glk_request_hyperlink_event(window)
  @glk 258 _vararg_count 0;
  return 0;
];

[ glk_cancel_hyperlink_event _vararg_count;
  ! glk_cancel_hyperlink_event(window)
  @glk 259 _vararg_count 0;
  return 0;
];

[ glk_buffer_to_lower_case_uni _vararg_count ret;
  ! glk_buffer_to_lower_case_uni(uintarray, arraylen, uint) => uint
  @glk 288 _vararg_count ret;
  return ret;
];

[ glk_buffer_to_upper_case_uni _vararg_count ret;
  ! glk_buffer_to_upper_case_uni(uintarray, arraylen, uint) => uint
  @glk 289 _vararg_count ret;
  return ret;
];

[ glk_buffer_to_title_case_uni _vararg_count ret;
  ! glk_buffer_to_title_case_uni(uintarray, arraylen, uint, uint) => uint
  @glk 290 _vararg_count ret;
  return ret;
];

[ glk_buffer_canon_decompose_uni _vararg_count ret;
  ! glk_buffer_canon_decompose_uni(uintarray, arraylen, uint) => uint
  @glk 291 _vararg_count ret;
  return ret;
];

[ glk_buffer_canon_normalize_uni _vararg_count ret;
  ! glk_buffer_canon_normalize_uni(uintarray, arraylen, uint) => uint
  @glk 292 _vararg_count ret;
  return ret;
];

[ glk_put_char_uni _vararg_count;
  ! glk_put_char_uni(uint)
  @glk 296 _vararg_count 0;
  return 0;
];

[ glk_put_string_uni _vararg_count;
  ! glk_put_string_uni(unicode)
  @glk 297 _vararg_count 0;
  return 0;
];

[ glk_put_buffer_uni _vararg_count;
  ! glk_put_buffer_uni(uintarray, arraylen)
  @glk 298 _vararg_count 0;
  return 0;
];

[ glk_put_char_stream_uni _vararg_count;
  ! glk_put_char_stream_uni(stream, uint)
  @glk 299 _vararg_count 0;
  return 0;
];

[ glk_put_string_stream_uni _vararg_count;
  ! glk_put_string_stream_uni(stream, unicode)
  @glk 300 _vararg_count 0;
  return 0;
];

[ glk_put_buffer_stream_uni _vararg_count;
  ! glk_put_buffer_stream_uni(stream, uintarray, arraylen)
  @glk 301 _vararg_count 0;
  return 0;
];

[ glk_get_char_stream_uni _vararg_count ret;
  ! glk_get_char_stream_uni(stream) => int
  @glk 304 _vararg_count ret;
  return ret;
];

[ glk_get_buffer_stream_uni _vararg_count ret;
  ! glk_get_buffer_stream_uni(stream, uintarray, arraylen) => uint
  @glk 305 _vararg_count ret;
  return ret;
];

[ glk_get_line_stream_uni _vararg_count ret;
  ! glk_get_line_stream_uni(stream, uintarray, arraylen) => uint
  @glk 306 _vararg_count ret;
  return ret;
];

[ glk_stream_open_file_uni _vararg_count ret;
  ! glk_stream_open_file_uni(fileref, uint, uint) => stream
  @glk 312 _vararg_count ret;
  return ret;
];

[ glk_stream_open_memory_uni _vararg_count ret;
  ! glk_stream_open_memory_uni(uintarray, arraylen, uint, uint) => stream
  @glk 313 _vararg_count ret;
  return ret;
];

[ glk_request_char_event_uni _vararg_count;
  ! glk_request_char_event_uni(window)
  @glk 320 _vararg_count 0;
  return 0;
];

[ glk_request_line_event_uni _vararg_count;
  ! glk_request_line_event_uni(window, uintarray, arraylen, uint)
  @glk 321 _vararg_count 0;
  return 0;
];

[ glk_set_echo_line_event _vararg_count;
  ! glk_set_echo_line_event(window, uint)
  @glk 336 _vararg_count 0;
  return 0;
];

[ glk_set_terminators_line_event _vararg_count;
  ! glk_set_terminators_line_event(window, uintarray, arraylen)
  @glk 337 _vararg_count 0;
  return 0;
];

