import {Format} from "../../Format.js";

export class pl extends Format
{
	name           = "Perl Script";
	website        = "http://fileformats.archiveteam.org/wiki/Perl";
	ext            = [".pl"];
	forbidExtMatch = true;
	magic          = ["Perl script", "a /usr/local/perl script", "Shell Skript: '/usr/local/perl'", "Shell Skript: '/usr/local/bin/perl'", "Shell Skript: '/usr/bin/perl'", "application/x-perl", /^Shell Skript: .*perl.exe/, /^Perl\d module source/];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}
