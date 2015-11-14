xquery version "3.0";

declare namespace n="http://www.bbc.co.uk/nitro/";

declare option exist:serialize "method=xhtml media-type=application/csv";

declare function local:apply-pipes($sequence) {
    for $item in $sequence
        return
            if (index-of($sequence, $item) < count($sequence)) then
                concat(normalize-space($item),'|')
            else
                normalize-space($item)
};

declare function local:to-tsv($fragment) {
    let $tsv := concat(string-join($fragment/*/normalize-space(.), '&#9;'),'&#10;')
    return
        $tsv
};

let $header := "clip_pid&#9;version_pids&#9;clip_title&#9;genres&#9;formats&#9;episode_pid&#9;episode_title&#9;episode_master_brand&#9;series_pid&#9;series_title&#9;series_master_brand&#9;brand_pid&#9;brand_title&#9;brand_master_brand&#10;"

for $h in $header
    return
        ($h,
        for $doc in collection('/db/bbc_radio_four')/n:clip
            let $clip_pid := $doc/n:pid/text()
            let $clip_title := $doc/n:title/text()
            (: optional ancestors, possibly sequences > 1 :)
            let $ancestor_episodes := $doc/n:ancestors/n:episode
            let $ancestor_series := $doc/n:ancestors/n:series
            let $ancestor_brands := $doc/n:ancestors/n:brand
            (: possibly sequences > 1 :)
            let $version_pids := data($doc/n:versions/n:version/@pid)
            let $genres := distinct-values($doc/n:genre_groupings/n:genre_group//n:genre)
            let $programme_formats := $doc/n:programme_formats/n:format/text()
            return
                let $clip := 
                <clip>
                    <pid>{$clip_pid}</pid>
                    <version_pids>{local:apply-pipes($version_pids)}</version_pids>
                    <title>{$clip_title}</title>
                    <genres>{local:apply-pipes($genres)}</genres>
                    <formats>{local:apply-pipes($programme_formats)}</formats>
                    <episodes_pid>{local:apply-pipes($ancestor_episodes/n:pid/text())}</episodes_pid>
                    <episodes_title>{local:apply-pipes($ancestor_episodes/n:title/text())}</episodes_title>
                    <episodes_master_brand>{local:apply-pipes($ancestor_episodes/n:master_brand/@mid)}</episodes_master_brand>
                    <series_pid>{local:apply-pipes($ancestor_series/n:pid/text())}</series_pid>
                    <series_title>{local:apply-pipes($ancestor_series/n:title/text())}</series_title>
                    <series_master_brand>{local:apply-pipes($ancestor_series/n:master_brand/@mid)}</series_master_brand>
                    <brand_pid>{local:apply-pipes($ancestor_brands/n:pid/text())}</brand_pid>
                    <brand_title>{local:apply-pipes($ancestor_brands/n:title/text())}</brand_title>
                    <brand_master_brand>{local:apply-pipes($ancestor_brands/n:master_brand/@mid)}</brand_master_brand>
                </clip>
                return
                    local:to-tsv($clip)
        )