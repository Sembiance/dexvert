/*
import {Format} from "../../Format.js";

export class avr extends Format
{
	name = "Audio Visual Research";
	website = "http://fileformats.archiveteam.org/wiki/AVR";
	ext = [".avr"];
	magic = [{}];
	converters = ["sox","ffmpeg"]

	metaProviders = [""];
}
*/
/*
"use strict";
/* eslint-disable prefer-named-capture-group */
const XU = require("@sembiance/xu");

exports.meta =
{
	name    : "Audio Visual Research",
	website : "http://fileformats.archiveteam.org/wiki/AVR",
	ext     : [".avr"],
	magic   : [/^Audio Visual Research (file|sample)/]
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.converterPriority = ["sox", "ffmpeg"];

*/
