import {Format} from "../../Format.js";

export class unixShellScript extends Format
{
	name           = "Linux/UNIX/POSIX Shell Script";
	website        = "http://fileformats.archiveteam.org/wiki/Bourne_shell_script";
	ext            = [".sh", ".x11", ".gnu", ".csh", ".tsch"];
	forbidExtMatch = true;
	magic          = ["Linux/UNIX shell script", "POSIX shell script", "C shell script", "a /bin/csh script", "a /bin/sh script", "script text executable for", "Bourne-Again shell script text executable", "Shell Skript: '/bin/sh",
		"Shell Skript: '/bin/bash", "Shell Skript: '/bin/csh"];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
