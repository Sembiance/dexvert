import {Format} from "../../Format.js";

export class jovanLogicVI extends Format
{
	name           = "Jovian Logix VI Image";
	website        = "http://fileformats.archiveteam.org/wiki/Jovian_Logic_VI";
	ext            = [".vi"];
	forbidExtMatch = true;
	magic          = ["Jovian Logic VI bitmap", "deark: jovianvi"];
	converters     = ["deark[module:jovianvi]", "nconvert", "imageAlchemy[hasExtMatch]", "pv[hasExtMatch]"];
	verify         = ({meta}) => meta.width<7000 && meta.height<7000;
}
