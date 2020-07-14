"use strict";
const XU = require("@sembiance/xu");

exports.meta =
{
	name             : "Covox ADPCM Encoded Audio",
	website          : "https://wiki.multimedia.cx/index.php/Covox_ADPCM",
	ext              : [".v8", ".cvx"],
	magic            : ["Covox ADPCM encoded audio"],
	unsupported      : true,
	unsupportedNotes : XU.trim`
		I've tried using C:\\APP\\COVOXCONV.EXE but it could never get the WAV output at the correct sample rate, despire me trying different ones
		I also tried C:\\SPUT111\\SPUT.COM but it appears only output more COVOX formats.
		According to that wiki, mplayer might be able to play these, but I couldn't get it to play any of them.`
};
