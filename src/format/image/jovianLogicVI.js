import {Format} from "../../Format.js";

export class jovianLogicVI extends Format
{
	name           = "Jovian Logix VI Image";
	website        = "http://fileformats.archiveteam.org/wiki/Jovian_Logic_VI";
	ext            = [".vi"];
	forbidExtMatch = true;
	magic          = ["Jovian Logic VI bitmap", "deark: jovianvi", "Jovian VI :vi:"];
	converters     = ["deark[module:jovianvi]", "nconvert[format:vi]", "imageAlchemy[hasExtMatch]", "pv[hasExtMatch]"];
	verify         = ({meta}) => meta.width>2 && meta.height>2 && meta.width<7000 && meta.height<7000;
}
