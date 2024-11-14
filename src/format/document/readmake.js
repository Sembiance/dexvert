import {Format} from "../../Format.js";

const _READMAKE_MAGIC = ["16bit DOS READMAKE executable"];
export {_READMAKE_MAGIC};

export class readmake extends Format
{
	name           = "READMAKE";
	website        = "http://fileformats.archiveteam.org/wiki/READMAKE";
	ext            = [".exe"];
	forbidExtMatch = true;
	magic          = _READMAKE_MAGIC;
	converters     = ["deark[module:readmake][opt:text:encconv=0]"];
}
