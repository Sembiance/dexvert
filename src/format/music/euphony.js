import {Format} from "../../Format.js";

export class euphony extends Format
{
	name         = "EUPHONY Module";
	website      = "http://fileformats.archiveteam.org/wiki/EUPHONY";
	ext          = [".eup", ".fmb", ".pmb"];
	fileSize     = {".fmb" : 6152};
	keepFilename = true;

	// .eup files may require various .fmb/.pmb files, not sure which ones, so just include them all
	auxFiles = (input, otherFiles) =>
	{
		if([".fmb", ".pmb"].includes(input.ext.toLowerCase()))
			return [];
		
		const f = otherFiles.filter(otherFile => [".fmb", ".pmb"].includes(otherFile.ext.toLowerCase()));
		return f.length>0 ? f : false;
	};

	// Don't do anything with .fmb/.pmb files
	untouched       = ({f}) => [".fmb", ".pmb"].includes(f.input.ext.toLowerCase());
	verifyUntouched = false;
	metaProvider    = ["musicInfo"];
	converters      = ["eupplay"];
}
