import {Format} from "../../Format.js";

export class quartetST extends Format
{
	name          = "Quartet ST Module";
	ext           = [".qts", ".smp", ".4sq"];
	magic         = ["Quartet ST module"];
	matchPreExt   = true;
	keepFilename  = true;
	metaProvider  = ["musicInfo"];

	// Both .qts and .smp are required and are often prefix extensions
	auxFiles = (input, otherFiles) =>
	{
		const preExtMatch = this.ext.some(ext => ext.toLowerCase()===input.preExt.toLowerCase());
		const otherExt = this.ext.find(ext => ext!==(preExtMatch ? input.preExt : input.ext));
		return otherFiles.filter(file => (preExtMatch ? file.preName.toLowerCase()===input.preName.toLowerCase() : file.name.toLowerCase()===input.name.toLowerCase()) && otherExt===(preExtMatch ? file.preExt : file.ext));
	};

	// Don't do anything with .smp files
	untouched = ({f}) => (f.input.ext.toLowerCase() || f.input.preExt.toLowerCase())===".smp";

	converters = ["uade123[player:Quartet_ST]"];
	notes      = "Are there 2 seperate formats I'm dealing with here?";
}
