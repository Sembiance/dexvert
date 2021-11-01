/*
import {Format} from "../../Format.js";

export class fantavision extends Format
{
	name = "Fantavision Movie";
	ext = [".mve"];
	magic = ["Fantavision Movie"];
	weakMagic = true;
	notes = "\nPLAYER.EXE just loops the video forever, haven't figured out a way to get it to stop after playing once. So I just record for 40 seconds and that's the result.\nAlso, there is sound effects but my runUtil Xvfb doesn't support sound recording yet, so no sound.\nI just run DOSbox and record the screen, so there is dosbox logo at the start.";
	converters = ["fantavsn"]
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name      : "Fantavision Movie",
	ext       : [".mve"],
	magic     : ["Fantavision Movie"],
	weakMagic : true,
	notes     : XU.trim`
		PLAYER.EXE just loops the video forever, haven't figured out a way to get it to stop after playing once. So I just record for 40 seconds and that's the result.
		Also, there is sound effects but my runUtil Xvfb doesn't support sound recording yet, so no sound.
		I just run DOSbox and record the screen, so there is dosbox logo at the start.`
};

exports.converterPriority = ["fantavsn"];

*/
