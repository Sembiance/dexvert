import {Format} from "../../Format.js";

export class unixShellScript extends Format
{
	name           = "Linux/UNIX/POSIX Shell Script";
	website        = "http://fileformats.archiveteam.org/wiki/Bourne_shell_script";
	ext            = [".sh", ".x11", ".gnu", ".csh", ".tsch"];
	forbidExtMatch = true;
	magic          = ["Linux/UNIX shell script", "POSIX shell script", "C shell script", "a /bin/csh script", "script text executable for"];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
