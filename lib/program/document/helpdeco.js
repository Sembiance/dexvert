"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	fs = require("fs"),
	path = require("path"),
	tiptoe = require("tiptoe");

exports.meta =
{
	website       : "https://sourceforge.net/projects/helpdeco/",
	gentooPackage : "app-arch/helpdeco",
	gentooOverlay : "dexvert"
};

exports.bin = () => "helpdeco";

exports.pre = (state, p, r, cb) =>
{
	state.helpdecoTmpDirPath = fileUtil.generateTempFilePath(state.tmpDir);
	fs.mkdir(state.helpdecoTmpDirPath, {recursive : true}, cb);
};

exports.args = (state, p, r, inPath=state.input.absolute) => (["-r", "-y", inPath]);
exports.runOptions = state => ({cwd : state.helpdecoTmpDirPath, timeout : XU.MINUTE*4});

const fldinstRegex = /{\\field\s+{\\\*\\fldinst\s+import\s+(?<fileName>[^}]+)}}/;

// WARNING: The below is somewhat fragile, especially with the image converting that is taking place
exports.post = (state, p, r, cb) =>
{
	tiptoe(
		function locateRTF()
		{
			fileUtil.glob(state.helpdecoTmpDirPath, "*.rtf", {nodir : true}, this);
		},
		function loadRTF(rtfFilePaths=[])
		{
			if(rtfFilePaths.length!==1)
				return this.jump(-1);

			this.data.rtfFilePath = rtfFilePaths[0];

			fs.readFile(rtfFilePaths[0], XU.UTF8, this);
		},
		function convertImagesToPDF(rtfRaw)
		{
			this.data.rtfLines = rtfRaw.toString("utf8").split("\n");
			this.data.bitmapFilePaths = [];

			this.data.rtfLines.forEach(line =>
			{
				const parts = line.match(fldinstRegex);
				if(!parts)
					return;
				
				this.data.bitmapFilePaths.push(path.join(state.helpdecoTmpDirPath, parts.groups.fileName));
			});

			if(this.data.bitmapFilePaths.length===0)
				return this.jump(-2);
			
			// Convert SHG files
			this.data.bitmapFilePaths.parallelForEach((bitmapFilePath, subcb) =>
			{
				if(bitmapFilePath.endsWith(".shg"))
					p.util.program.run("deark", {argsd : [bitmapFilePath, state.helpdecoTmpDirPath, path.basename(bitmapFilePath)]})(state, p, subcb);
				else
					setImmediate(subcb);
			}, this);
		},
		function convertToPNG()
		{
			this.data.bitmapFilePaths.parallelForEach((bitmapFilePath, subcb) =>
			{
				if(bitmapFilePath.endsWith(".shg"))
					p.util.program.run("convert", {argsd : [`${bitmapFilePath}.000.bmp`, `${bitmapFilePath}.png`]})(state, p, subcb);
				else
					p.util.program.run("convert", {argsd : [bitmapFilePath, `${bitmapFilePath}.png`]})(state, p, subcb);
			}, this);
		},
		function loadImages()
		{
			this.data.bitmapFilePaths.parallelForEach((bitmapFilePath, subcb) => fs.readFile(`${bitmapFilePath}.png`, subcb), this);
		},
		function embedImagesIntoRTF(imagesFileData)
		{
			let i=0;
			fs.writeFile(this.data.rtfFilePath, this.data.rtfLines.map(line =>
			{
				if(!line.match(fldinstRegex))
					return line;

				return line.replace(fldinstRegex, `{\\pict\\pngblip\n${imagesFileData[i++].toString("hex").toLowerCase()}}`);
			}).join("\n"), XU.UTF8, this);
		},
		function convertRTFToPDF()
		{
			state.unoconvType = "pdf";
			p.util.program.run("unoconv", {argsd : [this.data.rtfFilePath]})(state, p, this);
		},
		function cleanup()
		{
			delete state.unoconvType;
			fileUtil.unlink(state.helpdecoTmpDirPath, this);
		},
		cb
	);
};
