import {Format} from "../../Format.js";

export class grasp extends Format
{
	name       = "GRASP Animation Archive";
	website    = "http://fileformats.archiveteam.org/wiki/GRASP_GL";
	ext        = [".gl"];
	magic      = ["GRASP animation"];
	idMeta     = ({macFileType}) => macFileType==="GL  ";
	weakMagic  = true;
	notes      = "Several GL files don't play correctly with GRASP4 (PENCIL.GL, ROCKET.GL, SCISSORS.GL, KITE.GL, ACORN.GL, UMBRELLA.GL, v7vga.gl, l&hardy.gl, ICE.GL, COUNT.GL, LEAF.GL), likely need a later version.";
	converters = ["grasp4"];

	// this ensures random .gl files don't produce garbage, duration must be at least 300ms
	verify    = ({meta}) => (meta.duration || 0)>=300;
}
