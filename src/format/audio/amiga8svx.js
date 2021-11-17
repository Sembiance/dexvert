/*
import {Format} from "../../Format.js";

export class amiga8svx extends Format
{
	name = "Amiga 8-bit Sampled Voice";
	website = "http://fileformats.archiveteam.org/wiki/8SVX";
	ext = [".8svx",".iff"];
	weakExt = [".iff"];
	magic = ["Amiga IFF 8SVX audio","IFF data, 8SVX","Interchange File Format 8-bit Sampled Voice"];
	notes = "Some 8SVX files don't have a sample rate in the file (test3.iff, sample01.ek___D.8svx). In these cases I try multiple different common sample rates.";
	converters = [{"program":"ffmpeg"},"8SVXtoXXX"]

inputMeta = undefined;

preSteps = [null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs");

exports.meta =
{
	name    : "Amiga 8-bit Sampled Voice",
	website : "http://fileformats.archiveteam.org/wiki/8SVX",
	ext     : [".8svx", ".iff"],
	weakExt : [".iff"],
	magic   : ["Amiga IFF 8SVX audio", "IFF data, 8SVX", "Interchange File Format 8-bit Sampled Voice"],
	notes   : "Some 8SVX files don't have a sample rate in the file (test3.iff, sample01.ek___D.8svx). In these cases I try multiple different common sample rates."
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.preSteps = [
	() => (state, p, cb) =>
	{
		tiptoe(
			function loadFileData()
			{
				fs.readFile(state.input.absolute, this);
			},
			function checkForNullSampleRate(inputBuffer)
			{
				const vhdrLoc = inputBuffer.indexOf("VHDR");
				if(vhdrLoc!==-1)
				{
					const offsetLoc = vhdrLoc+20;
					const fileRate = inputBuffer.readUInt16BE(offsetLoc);
					if(fileRate===1)
					{
						// 1Hz is likely meant to be 8khz
						state.voiceRate = 8000;	// 8000, 11025, 16000, 22050, 32000, 37800, 44100, 48000
					}
					else if(fileRate===0)
					{
						// 0Hz is a bug and ffmpeg won't even convert them. So we fill in a sample rate and cross our fingers
						state.tmpVoiceFilePath = fileUtil.generateTempFilePath(state.cwd, ".8svx");
						inputBuffer.writeUInt16BE(8000, offsetLoc);
						return fs.writeFile(state.tmpVoiceFilePath, inputBuffer, this);
					}
				}
				
				this();
			},
			cb
		);
	}
];

exports.converterPriority = [{program : "ffmpeg", argsd : state =>
{
	const rargs = [];
	if(state.tmpVoiceFilePath)
		rargs.push(state.tmpVoiceFilePath);

	return rargs;
}, flags : state =>
{
	const rflags = {};
	if(state.voiceRate)
	{
		rflags.ffmpegExt = ".wav";
		rflags.ffmpegRate = state.voiceRate;
	}

	delete state.voiceRate;
	
	return rflags;
}}, "8SVXtoXXX"];

*/
