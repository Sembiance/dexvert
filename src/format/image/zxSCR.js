/*
import {Format} from "../../Format.js";

export class zxSCR extends Format
{
	name = "ZX Spectrum Standard SCR";
	website = "https://zxart.ee/eng/graphics/database/pictureType:standard/";
	ext = [".scr"];
	fileSize = 6912;

	mimeType = "image/x-zx-spectrum-standard-screen";
	notes = "Some files are originally animated (S.O.M. Tetris and lenn1st) but converters don't support this.";
	converters = ["recoil2png","convert","nconvert",`abydosconvert[format:${this.mimeType}]`]

	metaProvider = [""];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name                : "ZX Spectrum Standard SCR",
	website             : "https://zxart.ee/eng/graphics/database/pictureType:standard/",
	ext                 : [".scr"],
	fileSize            : 6912,
	forbidFileSizeMatch : true,
	mimeType            : "image/x-zx-spectrum-standard-screen",
	notes               : "Some files are originally animated (S.O.M. Tetris and lenn1st) but converters don't support this."
};

exports.converterPriority = ["recoil2png", "convert", "nconvert", `abydosconvert[format:${this.mimeType}]`];

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

*/
