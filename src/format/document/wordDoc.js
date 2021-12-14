import {Format} from "../../Format.js";

export class wordDoc extends Format
{
	name           = "Word Document";
	website        = "http://fileformats.archiveteam.org/wiki/DOC";
	ext            = [".doc"];
	forbidExtMatch = true;
	magic          = ["Microsoft Word document", "Microsoft Word for Windows"];
	converters     = ["fileMerlin", "antiword", "soffice"];
	post = dexState =>
	{
		Object.assign(dexState.meta, dexState.ran.find(({programid}) => programid==="antiword")?.meta || {});
		if(dexState.meta.passwordProtected)
		{
			// can't do this in a 'untouched' callback because this meta data isn't available until after antiword converter has ran and the untouched method is called before converters
			dexState.untouched = true;
			dexState.processed = true;
			return true;
		}

		return false;
	};
}
