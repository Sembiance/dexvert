import {Format} from "../../Format.js";

export class hyperWriter extends Format
{
	name           = "HyperWriter";
	website        = "http://fileformats.archiveteam.org/wiki/Hyperwriter";
	ext            = [".hw4", ".hw3"];
	forbidExtMatch = true;
	magic          = ["HyperWriter document"];
	auxFiles = (input, otherFiles) =>
	{
		if(input.ext.toLowerCase()!==".hw4")
			return false;

		// .hw4 is usually paired with a .hwn of the same name, required for some like _STARTUP to show up correctly. Not sure what the other supporting files are for, but include em
		const supportingFiles = otherFiles.filter(file => [".hwa", ".hwi", ".hwn", ".hwt"].some(v => file.base.toLowerCase()===`${input.name.toLowerCase()}${v}`));
		return supportingFiles?.length ? supportingFiles : false;
	};

	converters = r => [({".hw4" : "hyperReader4", ".hw3" : "hyperReader3"}[r.f.input.ext.toLowerCase()] || "hyperReader4")];
}
