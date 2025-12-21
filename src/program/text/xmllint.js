import {Program} from "../../Program.js";

export class xmllint extends Program
{
	website = "https://gitlab.gnome.org/GNOME/libxml2/-/wikis/home";
	package = "dev-libs/libxml2";
	flags   = {
		ext    : "Ensure the output file has a specific extension"
	};
	bin        = "xmllint";
	unsafe     = true;
	args       = r => ["--recover", r.inFile()];
	runOptions = async r => ({stdoutFilePath : await r.outFile(`out${r.flags.ext || ".xml"}`)});
	renameOut  = true;
}
