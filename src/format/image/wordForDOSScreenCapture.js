import {Format} from "../../Format.js";

export class wordForDOSScreenCapture extends Format
{
	name       = "Word for DOS Screen Capture";
	website    = "http://fileformats.archiveteam.org/wiki/Word_for_DOS_screen_capture";
	ext        = [".scr", ".mwg"];
	magic      = ["deark: mswordscr (Word for DOS screen capture)"];
	converters = ["deark[module:mswordscr]"];
}
