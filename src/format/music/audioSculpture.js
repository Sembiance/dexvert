import {Format} from "../../Format.js";

export class audioSculpture extends Format
{
	name         = "Audio Sculpture Module";
	website      = "http://fileformats.archiveteam.org/wiki/Audio_Sculpture";
	ext          = [".adsc", ".as"];
	magic        = ["Audio Sculpture module"];
	keepFilename = true;

	auxFiles = (input, otherFiles) =>
	{
		// Needs both file.adsc and file.adsc.as however only the .adsc file is converted
		const otherFile = otherFiles.find(file => (input.ext.toLowerCase()===".adsc" ? file.base.toLowerCase()===`${input.base.toLowerCase()}.as` : file.ext.toLowerCase()===".adsc" && file.base.toLowerCase()===input.name.toLowerCase()));
		return otherFile ? [otherFile] : [];
	};

	// Don't do anything with .as files
	untouched       = ({f}) => f.input.ext.toLowerCase()===".as";
	verifyUntouched = false;

	metaProvider  = ["musicInfo"];
	converters    = ["uade123[player:AudioSculpture]"];
}
