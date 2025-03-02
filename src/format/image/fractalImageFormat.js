import {Format} from "../../Format.js";

export class fractalImageFormat extends Format
{
	name           = "Fractal Image Format";
	website        = "http://fileformats.archiveteam.org/wiki/Fractal_Image_Format";
	ext            = [".fif"];
	forbidExtMatch = true;
	magic          = ["Fractal Image Format bitmap", /^x-fmt\/320( |$)/];
	idMeta         = ({macFileType, macFileCreator}) => macFileType==="FIF " && macFileCreator==="FIFd";
	converters     = ["fifView", "graphicWorkshopProfessional"];
	notes          = "The 256C versions don't convert with any program I could find. With GenuineFractal 4 (GF-PP4-TR-Win32.exe) and PS7 (app/ps7.zip) I was not able to open any .fif files.";
}
