<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" encoding="UTF-8" />
    <xsl:template match="/">
        <xsl:text>trip_id, stop_sequence, stop_id, arrival_time, departure_time&#10;</xsl:text>
        <xsl:for-each select="TransXChange/VehicleJourneys/VehicleJourney">
    
            <xsl:variable name="vjc" select="VehicleJourneyCode"/>
            <xsl:variable name="sr" select="ServiceRef"/>
            <xsl:variable name="depTime" select="DepartureTime"/>
            <!-- <xsl:value-of select="DepartureTime"/><xsl:text>,</xsl:text> -->
            
            <xsl:variable name="jpref" select="JourneyPatternRef"/>
            <xsl:for-each select="../../Services/Service/StandardService/JourneyPattern">
                <xsl:if test="./@id = $jpref">
                    <xsl:variable name="jpsref" select="JourneyPatternSectionRefs"/>
                    <xsl:for-each select="../../../../JourneyPatternSections/JourneyPatternSection">
                    <!-- <xsl:text>hello</xsl:text> -->
                        <xsl:if test="./@id = $jpsref">
                            <xsl:for-each select="JourneyPatternTimingLink">
                                <xsl:value-of select="$sr"/><xsl:text>-</xsl:text><xsl:value-of select="$vjc"/><xsl:text>,</xsl:text>
                                <xsl:value-of select="From/@SequenceNumber"/><xsl:text>,</xsl:text>
                                <xsl:value-of select="From/StopPointRef"/><xsl:text>,</xsl:text>
                                <xsl:value-of select="$depTime"/><xsl:text>,</xsl:text>
                                <xsl:choose>
                                    <xsl:when test="From/WaitTime">
                                        <xsl:value-of select="From/WaitTime"/><xsl:text>,</xsl:text>
                                    </xsl:when>
                                    <xsl:otherwise><xsl:text>PT0S,</xsl:text></xsl:otherwise>
                                </xsl:choose>
                                <xsl:value-of select="RunTime"/><xsl:text>&#10;</xsl:text>
                                <xsl:if test="position() = last()">
                                    <xsl:value-of select="$sr"/><xsl:text>-</xsl:text><xsl:value-of select="$vjc"/><xsl:text>,</xsl:text><xsl:value-of select="To/@SequenceNumber"/><xsl:text>,</xsl:text><xsl:value-of select="To/StopPointRef"/><xsl:text>,</xsl:text><xsl:value-of select="$depTime"/><xsl:text>,</xsl:text><xsl:value-of select="$depTime"/><xsl:text>&#10;</xsl:text>
                                </xsl:if>
                            </xsl:for-each>
                        </xsl:if>
                    </xsl:for-each>
                </xsl:if>
            </xsl:for-each>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>