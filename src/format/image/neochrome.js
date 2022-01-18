import {Format} from "../../Format.js";

export class neochrome extends Format
{
	name     = "Neochrome";
	website  = "http://fileformats.archiveteam.org/wiki/NEOchrome";
	ext      = [".neo", ".rst"];
	mimeType = "image/x-neo";
	fileSize = {".neo" : 32128};
	auxFiles = (input, otherFiles) =>
	{
		// .neo can convert on it's own, but optionally uses an .rst
		const otherFile = otherFiles.find(file => file.base.toLowerCase()===(input.name.toLowerCase() + this.ext.find(ext => ext!==input.ext.toLowerCase())));
		return otherFile ? [otherFile] : false;
	};

	// Don't do anything with .rst files
	untouched       = ({f}) => f.input.ext.toLowerCase()===".rst";
	verifyUntouched = false;
	converters      = ["recoil2png", "nconvert", `abydosconvert[format:${this.mimeType}]`];
}
