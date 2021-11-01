/*
import {Format} from "../../Format.js";

export class rol extends Format
{
	name = "AdLib/Roland Song";
	website = "http://fileformats.archiveteam.org/wiki/AdLib_Visual_Composer_/_Roland_Synthesizer_song";
	ext = [".rol"];
	magic = ["AdLib Visual Composer music"];
	notes = "Couldn't convert GIRLIPEN.ROL for some reason";

steps = [null,null,null];
}
*/
/*
"use strict";
const XU = require("@sembiance/xu"),
	path = require("path"),
	tiptoe = require("tiptoe"),
	fs = require("fs"),
	fileUtil = require("@sembiance/xutil").file;

exports.meta =
{
	name    : "AdLib/Roland Song",
	website : "http://fileformats.archiveteam.org/wiki/AdLib_Visual_Composer_/_Roland_Synthesizer_song",
	ext     : [".rol"],
	magic   : ["AdLib Visual Composer music"],
	notes   : "Couldn't convert GIRLIPEN.ROL for some reason"
};

const ROL_BANK_DIR_PATH = path.join(__dirname, "..", "..", "..", "music", "rolBank");

exports.steps =
[
	() => (state, p, cb) =>
	{
		const tmpWorkDir = fileUtil.generateTempFilePath();

		tiptoe(
			function findBankFile()
			{
				fileUtil.glob(path.dirname(state.input.absolute), "*.bnk", {nodir : true, nocase : true}, this.parallel());
				fileUtil.glob(ROL_BANK_DIR_PATH, "*", {nodir : true, nocase : true}, this.parallel());
				fs.mkdir(tmpWorkDir, {recursive : true}, this.parallel());
			},
			function prepareBankFiles(bankFilePaths, standardBankFilePaths)
			{
				[...bankFilePaths, ...standardBankFilePaths].serialForEach((bankFilePath, subcb) =>
				{
					const destBankFilePath = path.join(tmpWorkDir, path.basename(bankFilePath).toLowerCase());
					if(fs.existsSync(destBankFilePath))
						return setImmediate(subcb);

					fs.symlink(bankFilePath, destBankFilePath, subcb);
				}, this.parallel());

				fs.copyFile(state.input.absolute, path.join(tmpWorkDir, "in.rol"), this.parallel());
			},
			function performConversion()
			{
				p.util.program.run("adplay", {argsd : ["./in.rol", "./outfile.wav"], runOptions : {cwd : tmpWorkDir}})(state, p, this);
			},
			function cleanup()
			{
				if(!fileUtil.existsSync(path.join(tmpWorkDir, "outfile.wav")))
					return this();

				fileUtil.move(path.join(tmpWorkDir, "outfile.wav"), path.join(state.output.absolute, `${state.input.name}.wav`), this);
			},
			function removeWorkDir()
			{
				fileUtil.unlink(tmpWorkDir, this);
			},
			cb
		);
	},
	(state, p) => p.util.file.findValidOutputFiles(),
	(state, p) => p.family.validateOutputFiles
];

*/
