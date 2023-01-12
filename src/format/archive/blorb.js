import {Format} from "../../Format.js";

export class blorb extends Format
{
	name           = "Blorb Interactive Fiction Package";
	website        = "http://justsolve.archiveteam.org/wiki/Blorb";
	ext            = [".blorb", ".gblorb", ".zblorb", ".blb", ".glb", ".zlb"];
	forbidExtMatch = [".blb", ".glb", ".zlb"];
	magic          = ["Blorb interactive fiction package", "IFF data, Blorb Interactive Fiction"];
	converters     = ["blorbtar"];
}
