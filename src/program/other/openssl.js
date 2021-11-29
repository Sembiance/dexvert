
import {Program} from "../../Program.js";

export class openssl extends Program
{
	website        = "https://www.openssl.org/";
	gentooPackage  = "dev-libs/openssl";
	gentooUseFlags = "asm zlib";
	unsafe         = true;
	flags          =
	{
		command  : "Which command to perform. REQUIRED FLAG",
		encoding : "Encoding type of the certificate. Default: Let openssl decide (usually fails)"
	};
	bin  = "openssl";
	args = r =>
	{
		const a = [r.flags.command, "-noout", "-text"];
		if(r.flags.encoding)
			a.push("-inform", r.flags.encoding);
			
		return [...a, "-in", r.inFile()];
	};
	runOptions = async r => ({stdoutFilePath : await r.outFile("out.txt")});
}
