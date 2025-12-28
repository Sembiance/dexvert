<?php
/**
 * Initiates the extraction process and read the P3T/RAF file
 * @package PS3Theme.net
 * @subpackage P3T Extractor
 * @access public
 * @author Hoshang Sadiq
 * @copyright 2011
 * @todo don't make a temporary file for RAF
 * @todo all fields are public, should really be private with setters and if required getters
 */

namespace P3TExtractor;

class Element
{
    /**
     * Contains the number of attributes this element has
     * @var int
     */
    public $numattr = 0;

    /**
     * Contains the offset where the first element is stored
     * @var int
     */
    public $stringoffset = 0;

    /**
     * Contains the offset of the parent element
     * @var int
     */
    public $parentoffset = 0;

    /**
     * Contains the offset this element
     * @var int
     */
    public $offset = 0;

    /**
     * Contains an array of all the attributes
     * @var array
     */
    public $attribs = array();

    /**
     * Determines if this element contains any attributes
     * @var int
     */
    public $has_file = 0;

    /**
     * Contains the filename if it has any files
     * @var string
     */
    public $filename = '';

    /**
     * Contains the name of this tag
     * @var string
     */
    public $tagName = '';

    /**
     * Contains the Header original created in Extractor
     * @var Header
     */
    public $header;

    /**
     * Contains an array of subelements
     * @var Element[]
     */
    public $elemap = array();

    /**
     * Construct the element, requires a populated Header class
     * @param Header $header An instance of Header containing header information of the file
     */
    public function __construct(&$header)
    {
        $this->header = & $header;
    }

    /**
     * Add a sub-element.
     * @param Element $ele The sub element
     */
    public function appendChild($ele)
    {
        if (!isset($ele->offset)) {
            var_dump($ele);
        }
        $this->elemap[$ele->offset] = $ele;
    }

    /**
     * Add a attribute
     * @param Attribute $attr The attribute
     */
    public function setAttribute($attr)
    {
        if ($attr->type == 6) {
            $this->has_file = 1;
        }
        $this->attribs[$attr->name] = $attr;
    }

    /**
     * Dump the files and construct the XML, dumping the XML will not work if this
     * hasn't run yet, whether with or without extracting files.
     * This will recursively call all sub-elements' dump_files() function too.
     *
     * @param string $rootdir The directory to save the files to
     * @param resource $hfile An resource linked to fopen()
     * @param boolean $echo Whether or not to echo the status of the extraction
     * @param boolean $save Which files to save.
     * @return array
     * @throws \Exception
     *
     * @todo separate most, if not all of this code into a separate class/file
     */
    public function dump_files($rootdir, $hfile, $echo, $save = true)
    {
        $file_support = array('dynamic' => false, 'audio' => false);

        // Dump the children's files
        /** @var Element $element */
        foreach ($this->elemap as $element) {
            $support = $element->dump_files($rootdir, $hfile, $echo, $save);
            if ($support['dynamic'] === true) {
                $file_support['dynamic'] = true;
            }
            if ($support['audio'] === true) {
                $file_support['audio'] = true;
            }
        }

        // There are no files, we don't need to go further
        if ($this->has_file == 0) {
            return $file_support;
        }

        // attempt to create the extraction directory if not created
        if (!file_exists($rootdir) || !is_dir($rootdir)) {
            mkdir($rootdir);
            $this->header->custom('Extract directory not found, attempting to create it... ');
            if (!file_exists($rootdir)) {
                $this->header->failed();
                throw new \Exception('Unable to create directory: ' . $rootdir);
            }
            $this->header->success();
        }

        $pos = ftell($hfile);
        $fileoffset = $this->header->filetable_offset;

        // loop through the attributes
        foreach ($this->attribs as $v) {
            // only select the attributes with a file
            if ($v->type == 6) {
                // determine filetype, note, .png is also selected if .gim files are to saved.
                $ext = '.png'; // gim or png
                if ($this->tagName == 'bgimage') { // background
                    $ext = '.jpg'; // static background
                    if (isset($this->attribs['anim'])) { // dynamic background
                        $ext = '.raf';
                        $file_support['dynamic'] = true;
                    }
                } elseif ($this->tagName == 'se') { // audio files
                    $ext = '.vag';
                    $file_support['audio'] = true;
                } elseif ($this->header->magic === 'RAFO') { // static background resources
                    $ext = '';
                }

                // Determine the name
                if ($ext === '.vag') { // for audio we want file names like "audio_left.vag" and "audio_right.vag"
                    $filename = $rootdir . $this->attribs['id']->value . '_' . $v->name . $ext;
                } elseif (isset($this->attribs['id'])) { // if it has an ID
                    $filename = $rootdir . $this->attribs['id']->value . $ext;
                } elseif ($this->tagName == 'notification') { // notification would show "src.ext", replace that with notification.ext
                    $filename = $rootdir . $this->tagName . $ext;
                } else { // otherwise just use the name
                    $filename = $rootdir . $v->name . $ext;
                }

                // Determine if we need a suffix or not.
                // We need a suffix if this is a background image or the filename selected already exists
                if (file_exists($filename) || $this->tagName == 'bgimage') {
                    $suffix = 1;
                    while (true) {
                        if ($ext === '.vag') {
                            $filename = $rootdir . $this->attribs['id']->value . '_' . $v->name . '_' . $suffix . $ext;
                        } elseif (isset($this->attribs['id'])) {
                            $filename = $rootdir . $this->attribs['id']->value . '_' . $suffix . $ext;
                        } elseif ($this->tagName == 'notification') {
                            $filename = $rootdir . $this->tagName . '_' . $suffix . $ext;
                        } else {
                            $filename = $rootdir . $v->name . '_' . $suffix . $ext;
                        }
                        if (file_exists($filename)) {
                            $suffix++;
                        } else {
                            break;
                        }
                    }
                }

                // Set the internal file locater to the beginning of this file
                fseek($hfile, $fileoffset + $v->fileoffset);
                // read the file
                $cbuf = $v->filesize > 0 ? fread($hfile, $v->filesize) : '';
                $this->filename = $filename; // set this attribute's filename

                if ($ext !== '.raf') {
                    $this->header->write($filename);
                }
                if ($ext == '.png' && $cbuf != '') {
                    // zlib compressed image
                    $dbuf = gzuncompress($cbuf);
                    // convert .gim to .png
                    if ($save['png'] === true) {
                        try {
                            $gimfile = new Gim($dbuf);
                            $gimfile->save($filename);
                            $this->header->success();
                            unset($gimfile);
                        } catch (\Exception $e) {
                            $this->header->failed();
                            echo $e->getMessage();
                        }
                    } else {
                        $this->header->ignored();
                    }

                    // write original .gim file
                    $gim_file = substr($filename, 0, -4) . '.gim';
                    $this->header->write($gim_file);
                    if ($save['gim'] === true) {
                        try {
                            $outfile = fopen($gim_file, 'wb');
                            fwrite($outfile, $dbuf);
                            fclose($outfile);
                            $this->header->success();
                        } catch (\Exception $e) {
                            $this->header->failed();
                            echo $e->getMessage();
                        }
                    } else {
                        $this->header->ignored();
                    }
                    // RAF files, contains animation files for dynamic themes
                } elseif ($ext === '.raf' && ($save['raf'] === true || $save['gtf'] === true ||
                        $save['jsx'] === true || $save['edge'] === true || $save['skel'] === true)
                ) {
                    $this->parse_raf($cbuf, $rootdir, $echo, $save);
                } elseif ($ext === '.vag') {
                    $vag_file = '';

                    // if we require a .wav or a .vag file, we MUST save the vag file
                    // difference is if its JUST wav, we save it to a temporary file
                    // and delete it later, otherwise we save it to the proper file
                    if ($save['vag']) {
                        $vag_file = $filename;
                    } elseif ($save['wav'] === true) {
                        $vag_file = tempnam($rootdir, '.vag');
                    }

                    if ($save['vag'] || $save['wav']) {
                        try {
                            $outfile = fopen($vag_file, 'wb');
                            fwrite($outfile, $cbuf);
                            fclose($outfile);
                            if ($save['vag'] === true) {
                                $this->header->success();
                            }
                        } catch (\Exception $e) {
                            if ($save['vag'] === true) {
                                $this->header->failed();
                            }
                            echo $e->getMessage();
                        }
                    }
                    if ($save['vag'] !== true) {
                        $this->header->ignored();
                    }

                    $wav_file = substr($filename, 0, strrpos($filename, '.')) . '.wav';
                    $this->header->write($wav_file);

                    if ($save['wav'] === true) {
                        try {
                            new VAGConverter($vag_file, $wav_file);
                            $this->header->success();
                            // .wav takes priority over .vag in the xml
                            // as .vag can only be played by ps3
                            $this->filename = $wav_file;
                            if ($save['vag'] !== true) {
                                unlink($vag_file);
                            }
                        } catch (\Exception $e) {
                            $this->header->failed();
                            echo $e->getMessage();
                        }
                    } else {
                        $this->header->ignored();
                    }
                } else {
                    // write jpg, edge, skel, gtf, jsx
                    $four = substr($filename, strrpos($filename, '.') + 1, 4);
                    if ($four === 'edge' || $four === 'skel') {
                        $extension = $four;
                    } else {
                        $extension = substr($four, 0, 3);
                    }
                    if (isset($save[$extension]) && $save[$extension] === true) {
                        try {
                            $outfile = fopen($filename, 'wb');
                            fwrite($outfile, $cbuf);
                            fclose($outfile);
                            $this->header->success();
                        } catch (\Exception $e) {
                            $this->header->failed();
                            echo $e->getMessage();
                        }
                    } else {
                        $this->header->ignored();
                    }
                }
                $this->attribs[$v->name] = basename($this->filename);
            }
        }
        fseek($hfile, $pos); // reset the internal file pointer
        return $file_support;
    }

    /**
     * Parses the current data selected for this element
     * @param string $data The data for this element
     * @param string $format Format of the data to extract (used for php's unpack)
     * @param resource $hfile A resource of the fopen() for the P3T file
     */
    public function parse($data, $format, $hfile)
    {
        $f = $hfile;

        $this->offset = ftell($hfile) - strlen($data) - $this->header->tree_offset;

        $t = unpack($format, $data);
        //$this->t = $t;
        // 1st element is offset into string table
        $this->stringoffset = $t[0];

        // 2nd element is the no. of attributes
        $this->numattr = $t[1];

        // 3rd element is the offset of the parent element
        $this->parentoffset = $t[2];

        $pos = ftell($f);
        fseek($f, $this->header->stringtable_offset + $this->stringoffset);
        $a = fread($f, 1);
        while ($a != "\x00") {
            $this->tagName .= $a;
            $a = fread($f, 1);
        }
        fseek($f, $pos);
    }

    /**
     * This appends the XML version of this current element
     * @param  \DOMDocument $doc The DOMDocument to append this element
     * @param  bool|\DOMElement $element If a DOMElement is passed on here, the current
     *                                   element will be appended to this instead of $doc
     */
    public function saveXML($doc, $element = false)
    {
        $el = $doc->createElement($this->tagName);
        foreach ($this->attribs as $k => $v) {
            $v = (is_object($v)) ? $v->value : $v;
            // Skip size attributes
            // Size attributes contain the keyword size and contain only digits
            if (stripos($k, 'size') !== false && ctype_digit($v)) {
                continue;
            }
            $el->setAttribute($k, $v);
        }
        /** @var Element $element */
        foreach ($this->elemap as $child) {
            $child->saveXML($doc, $el);
        }
        if ($element) {
            $element->appendChild($el);
        } else {
            $doc->appendChild($el);
        }
    }

    /**
     * Basic RAF file layout
     * 8byte raf header (junk)
     * then p3t file compressed in zlib format
     *
     * p3t file contains .gtf file, which can then converted to .dds, and can be used
     * also contains .edge, .skel and .jsx
     * @param  string $raf_data The raf file data
     * @param  string $rootdir Where to save the new file
     * @param  bool $echo @see Extractor::__construct()
     * @param  array $save Array of file extensions to save
     */
    private function parse_raf($raf_data, $rootdir, $echo, $save)
    {
        // strip 8byte of raf header
        $raf_data = substr($raf_data, 8);
        $raf_data = gzuncompress($raf_data);
        $tmp = tempnam($rootdir, '.raf');

        $f = fopen($tmp, 'wb');
        fwrite($f, $raf_data);
        fclose($f);

        $raf = new Extractor($tmp, $rootdir, $echo);
        $raf->parse();
        $raf->dump_files($save);
        unlink($tmp);
    }
}
