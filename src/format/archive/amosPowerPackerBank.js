"use strict";
const XU = require("@sembiance/xu"),
	fileUtil = require("@sembiance/xutil").file,
	tiptoe = require("tiptoe"),
	fs = require("fs");

exports.meta =
{
	name    : "AMOS Power Packer Bank",
	ext     : [".abk"],
	magic   : ["AMOS PowerPacker bank"]
};

exports.converterPriority = ["xfdDecrunch"];

// xfdDecrunch leaves an amos bank file without a bank header, let's add it back in so we can properly identify the output files
exports.post = (state, p, cb) =>
{
	tiptoe(
		function findOutputFiles()
		{
			fileUtil.glob(state.output.absolute, "**", this);
		},
		function loadOutputFile(outputFilePaths)
		{
			// We assume just a single output file, if there is more than one, abort!
			if(outputFilePaths.length!==1)
				return this.finish();

			this.data.outputFilePath = outputFilePaths[0];

			fs.readFile(this.data.outputFilePath, {encoding : null}, this);
		},
		function saveOutputFile(outputData)
		{
			// Currently not bothering with putting in the bank length, most converters don't seem to care (tried music and picture, both work with 0 for the bank length)
			// Also not bothering putting the proper 'bank number' based on the type of format it is (music/picture/etc)
			// More details: https://www.exotica.org.uk/wiki/AMOS_file_formats
			const ambkHeader = Buffer.from([0x41, 0x6D, 0x42, 0x6B, 0x00, 0x03, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]);
			const fullBuffer = Buffer.concat([ambkHeader, outputData], ambkHeader.length+outputData.length);
			fs.writeFile(this.data.outputFilePath, fullBuffer, {encoding : null}, this);
		},
		cb
	);
};
