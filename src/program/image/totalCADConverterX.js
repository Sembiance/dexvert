import {Program} from "../../Program.js";

export class totalCADConverterX extends Program
{
	website = "https://www.coolutils.com/TotalCADConverterX";
	flags   = {
		// WARNING! I tried to do PNG and it complained about missing bcrypt.dll which is a Vista only file
		// So raster output may require Vista or higher
		outType : `Which format to transform into (svg pdf png, etc). See sandbox/app/totalCADXManual.txt for list. Default is: svg`
	};
	loc   = "winxp";
	bin   = "c:\\Program Files\\CoolUtils\\TotalCADConverterX\\CADConverterX.exe";
	args  = r => [r.inFile(), `c:\\out\\outfile.${r.flags.outputFileType || "svg"}`, "-WithoutBorder"];
	chain = r => ((r.flags.outType || "svg")==="svg" ? "deDynamicSVG" : null);
}
