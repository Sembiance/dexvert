/*
import {Format} from "../../Format.js";

export class grassSlideshow extends Format
{
	name = "Grass' Slideshow";
	website = "http://fileformats.archiveteam.org/wiki/Grass%27_Slideshow";
	ext = [".hpm"];
	converters = ["recoil2png"]

idCheck = undefined;
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	fs = require("fs");

exports.meta =
{
	name    : "Grass' Slideshow",
	website : "http://fileformats.archiveteam.org/wiki/Grass%27_Slideshow",
	ext     : [".hpm"]
};

// HPM from Atari is always 19203 size, but recoil2png does not support it
// So if we get to this format, we need to ensure that we don't try converting it because recoil2png will just produce garbage
exports.idCheck = state => fs.statSync(state.input.absolute).size!==19203;

exports.converterPriority = ["recoil2png"];

*/
