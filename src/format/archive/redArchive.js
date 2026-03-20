import {Format} from "../../Format.js";

export class redArchive extends Format
{
	name           = "RED Archive";
	website        = "http://fileformats.archiveteam.org/wiki/RED_(Knowledge_Dynamics)";
	ext            = [".red", ".lif", ".001", ".002", ".003", ".004"];
	forbidExtMatch = true;
	magic          = ["RED files library", "deark: red	"];
	auxFiles       = (input, otherFiles) =>
	{
		const supportingFiles = otherFiles?.filter(file => (/\.\d{3}$/).test(file.ext) || file.base.toLowerCase()==="install.dat");
		return supportingFiles?.length ? supportingFiles : false;
	};
	keepFilename = true;
	converters   = ["unred"];
}
