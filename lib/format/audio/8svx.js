"use strict";
const XU = require("@sembiance/xu"),
	tiptoe = require("tiptoe"),
	path = require("path"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs");

exports.meta =
{
	name    : "Amiga 8-bit Sampled Voice",
	website : "http://fileformats.archiveteam.org/wiki/8SVX",
	ext     : [".8svx", ".iff"],
	magic   : ["Amiga IFF 8SVX audio", "IFF data, 8SVX", "Interchange File Format 8-bit Sampled Voice"],
	notes : "Some 8SVX files don't have a sample rate in the file. In these cases I try multiple different common sample rates."
};

exports.inputMeta = (state, p, cb) => p.family.supportedInputMeta(state, p, cb);

exports.steps =
[
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
					if(inputBuffer.readUInt16BE(offsetLoc)===0)
					{
						// We don't have a valid sample rate, so ffmpeg and others will choke. So let's convert it with many different sample rates
						this.data.tmpFilePath = fileUtil.generateTempFilePath(state.tmpDirPath, ".8svx");
						return [8000, 11025, 16000, 22050, 32000, 37800, 44100, 48000].serialForEach((sampleRate, subcb) => convertWithSampleRate(this.data.tmpFilePath, inputBuffer, offsetLoc, sampleRate, subcb), this);
					}
				}

				// Fallback
				p.util.program.run("ffmpeg")(state, p, this);
			},
			function removeTmpFile()
			{
				if(!this.data.tmpFilePath)
					return this();
				
				fileUtil.unlink(this.data.tmpFilePath, this);
			},
			cb
		);

		function convertWithSampleRate(tmpFilePath, bufferData, offsetLoc, sampleRate, convertcb)
		{
			tiptoe(
				function writeTmpFile()
				{
					bufferData.writeUInt16BE(sampleRate, offsetLoc);
					fs.writeFile(tmpFilePath, bufferData, this);
				},
				function delay()
				{
					// Not sure why yet, but sometimes I only get a few of the above sample rates outputed instead of all 8. Adding this delay in to see if that helps? sigh.
					setTimeout(this, XU.SECOND/2);
				},
				function runConversion()
				{
					p.util.program.run("ffmpeg", {args : ["-i", tmpFilePath, path.join(state.output.dirPath, `${state.input.name}_${sampleRate}.wav`)]})(state, p, this);
				},
				convertcb
			);
		}
	}
];
