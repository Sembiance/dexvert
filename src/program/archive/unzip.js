import {xu} from "xu";
import {Program} from "../../Program.js";

export class unzip extends Program
{
	website = "http://infozip.sourceforge.net/";
	package = "app-arch/unzip";
	notes   = xu.trim`
		The version in dexvert overlay includes several patches such as:
		* Support for USE_SMITH via an unreduce_full.c patch from ftp://ftp.info-zip.org/pub/infozip/src/unreduce_full.zip
		* Custom patch to prevent archive comments (sample svga.exe) from forcing user input to continue extraction`;
	bin = "unzip";

	// By passing 'nopasswd' to -P it avoids the program hanging when an archive requires a password
	args = r => ["-od", r.outDir(), "-P", "nopasswd", r.inFile()];

	post = r =>
	{
		if(r.stderr.includes("incorrect password"))
			r.meta.passwordProtected = true;
	};
	renameOut = false;
}
