import {Format} from "../../Format.js";

const _WEAK_EXT = [".a", ".lib", ".sa"];

export class arArchive extends Format
{
	name           = "AR Archive";
	website        = "http://fileformats.archiveteam.org/wiki/AR";
	ext            = [".deb", ..._WEAK_EXT];
	forbidExtMatch = true;
	magic          = ["current ar archive", "ar archive", "Debian binary package", "Debian Linux Package", "Archive: Debian Software package", "BSD library", "Archive: The archiver", "application/x-archive", "application/vnd.debian.binary-package",
		/^MIPS archive /, /^Ar$/, /^archive$/, /^Alpha archive$/, "System V Release 1 ar archive", "deark: ar", /^fmt\/1835( |$)/];
	converters     = ["ar", "unar", "deark[module:ar]"];
	verify         = ({dexState, newFile}) =>
	{
		// So .a, .lib and .sa files just usually contain .o files which are not interesting at all (and libphobos2.a produces 9,999 files! which is a lot of noise)
		// So we fail validation on those files, but we also explictly set processed to true so that we still 'match' this format
		dexState.processed = true;
		return ![".symdef", ".o"].includes(newFile.ext.toLowerCase());
	};
}
