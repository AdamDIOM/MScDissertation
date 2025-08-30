<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="text" encoding="UTF-8" />
    <xsl:template match="/">
        <xsl:text>service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date&#10;</xsl:text>
        
        <xsl:for-each select="TransXChange/VehicleJourneys/VehicleJourney">
            <xsl:value-of select="ServiceRef"/><xsl:text>-</xsl:text><xsl:value-of select="VehicleJourneyCode"/><xsl:text>,</xsl:text>
            <xsl:if test="OperatingProfile/RegularDayType">
                <xsl:if test="OperatingProfile/RegularDayType/DaysOfWeek">
                    <xsl:text>DOW:</xsl:text>
                        <xsl:for-each select="OperatingProfile/RegularDayType/DaysOfWeek/*">
                            <xsl:value-of select="name()"/>
                            <xsl:if test="position() != last()">
                                <xsl:text>;</xsl:text>
                            </xsl:if>
                        </xsl:for-each>
                    <xsl:text>,</xsl:text>
                </xsl:if>
            </xsl:if>
            <xsl:if test="OperatingProfile/SpecialDaysOperation/DaysOfOperation">
                <xsl:text>SDO-OP:</xsl:text>
                        <xsl:for-each select="OperatingProfile/SpecialDaysOperation/DaysOfOperation/DateRange">
                            <xsl:value-of select="translate(StartDate,'-', '')"/><xsl:text>-</xsl:text><xsl:value-of select="translate(EndDate,'-', '')"/>
                            <xsl:if test="position() != last()">
                                <xsl:text>;</xsl:text>
                            </xsl:if>
                        </xsl:for-each>
                <xsl:text>,</xsl:text>
            </xsl:if>
            <xsl:if test="OperatingProfile/SpecialDaysOperation/DaysOfNonOperation">
                <xsl:text>SDO-NO:</xsl:text>
                        <xsl:for-each select="OperatingProfile/SpecialDaysOperation/DaysOfNonOperation/DateRange">
                            <xsl:value-of select="translate(StartDate,'-', '')"/><xsl:text>-</xsl:text><xsl:value-of select="translate(EndDate,'-', '')"/>
                            <xsl:if test="position() != last()">
                                <xsl:text>;</xsl:text>
                            </xsl:if>
                        </xsl:for-each>
                <xsl:text>,</xsl:text>
            </xsl:if>
            <xsl:if test="OperatingProfile/BankHolidayOperation/DaysOfOperation">
                <xsl:text>BHO-OP:</xsl:text>
                        <xsl:for-each select="OperatingProfile/BankHolidayOperation/DaysOfOperation/*">
                            <xsl:choose>
                                <xsl:when test="name() = 'OtherPublicHoliday'">
                                    <xsl:value-of select="translate(Date,'-', '')"/>
                                    <xsl:if test="position() != last()">
                                        <xsl:text>;</xsl:text>
                                    </xsl:if>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="name()"/>
                                    <xsl:if test="position() != last()">
                                        <xsl:text>;</xsl:text>
                                    </xsl:if>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:for-each>
                <xsl:text>,</xsl:text>
            </xsl:if>
            <xsl:if test="OperatingProfile/BankHolidayOperation/DaysOfNonOperation">
                <xsl:text>BHO-NO:</xsl:text>
                        <xsl:for-each select="OperatingProfile/BankHolidayOperation/DaysOfNonOperation/*">
                            <xsl:choose>
                                <xsl:when test="name() = 'OtherPublicHoliday'">
                                    <xsl:value-of select="translate(Date,'-', '')"/>
                                    <xsl:if test="position() != last()">
                                        <xsl:text>;</xsl:text>
                                    </xsl:if>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:value-of select="name()"/>
                                    <xsl:if test="position() != last()">
                                        <xsl:text>;</xsl:text>
                                    </xsl:if>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:for-each>
                <xsl:text>,</xsl:text>
            </xsl:if>
            <xsl:text>&#10;</xsl:text>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>