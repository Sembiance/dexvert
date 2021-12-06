import {Format} from "../../Format.js";

export class richardJoseph extends Format
{
	name           = "Richard Joseph Module/Instrument";
	website        = "http://fileformats.archiveteam.org/wiki/Richard_Joseph";
	ext            = [".sng", ".ins"];
	forbidExtMatch = true;
	magic          = ["RJP / Vectordean module", "RJP / Vectordean instrument"];
	keepFilename   = true;
	metaProvider   = ["musicInfo"];

	// Both .sng and .ins are required
	auxFiles = (input, otherFiles) => otherFiles.filter(file => file.base.toLowerCase()===(input.name.toLowerCase() + this.ext.find(ext => ext!==input.ext.toLowerCase())));

	// Don't do anything with .ins files
	untouched = ({f}) => f.input.ext.toLowerCase()===".ins";

	converters = ["uade123"];
}
