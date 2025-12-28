<?php

/**
 * Initiates the extraction process and read the P3T/RAF file
 * @package PS3Theme.net
 * @subpackage P3T Extractor
 * @access public
 * @author Hoshang Sadiq
 * @copyright 2011
 * @todo move parse into constructor.
 *
 * @version 1.1
 * @date 29/04/2011
 * @fixed Unnecessary variables were set
 * @fixed Undefined index when extracting RAF
 *
 * @changelog
 * @version 1.0
 * @date 23/01/2011
 */

namespace P3TExtractor;

class Attribute
{
    public $handle = 0;
    public $offset = 0;
    public $size = 0;
    public $value = 0;
    public $name = '';
    public $fileoffset = 0;
    public $filesize = 0;
    public $id = 0;
    public $type = 0;

    //public $t = 0;

    /**
     * Nothing to do in construction
     */
    public function __construct()
    {
    }

    /**
     * Read unpack chunk of data for this element.
     * @param string $data Binary string of data to unpack
     * @param Header $header The header class holding information of the P3T/RAF file
     * @param resource $hfile An fopen() handle
     */
    public function parse($data, $header, $hfile)
    {
        $f = $hfile;
        $pos = ftell($f);

        // find datatype and handle
        $t = unpack('N4', $data);
        $this->type = $atype = $t[1];
        $this->handle = $t[0];

        // unpack the information depending on the datatype
        if ($atype == 1) { // int
            $this->value = $t[2];
        } elseif ($atype == 2) { // float
            $t = unpack('N2/f/x4', $data);
            $this->value = isset($t[2]) ? $t[2] : $t[0];
        } elseif ($atype == 3) { // string
            $t = unpack('N4', $data);
            $this->offset = $t[2];
            $this->size = $t[3];
            fseek($f, $header->stringtable_offset + $this->offset);
            $this->value = ($this->size > 0) ? fread($f, $this->size) : '';
        } elseif ($atype == 6) { // filename
            $t = unpack('N4', $data);
            $this->fileoffset = $t[2];
            $this->filesize = $t[3];
        } elseif ($atype == 7) { // id
            $t = unpack('N3/x4', $data);
            $this->offset = $t[2];
            fseek($f, $header->idtable_offset + $this->offset);
            $id_bin = fread($f, 4);
            list($this->id) = unpack('N1', $id_bin);
            $this->value = '';
            $a = fread($f, 1);
            while ($a != "\x00") {
                $this->value = $this->value . $a;
                $a = fread($f, 1);
            }
        }

        // find the attribute name
        fseek($f, $header->stringtable_offset + $this->handle);
        $this->name = '';
        $a = fread($f, 1);
        // a null character seperates the attribute name 
        while ($a != "\x00") {
            $this->name = $this->name . $a;
            $a = fread($f, 1);
        }
        fseek($f, $pos);
    }
}

