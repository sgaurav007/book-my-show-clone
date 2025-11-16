package com.bookmyshow.common.utils;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public class DateUtils {

    private static final DateTimeFormatter DEFAULT_FORMATTER = DateTimeFormatter.ISO_LOCAL_DATE_TIME;

    public static String format(LocalDateTime dateTime) {
        return dateTime != null ? dateTime.format(DEFAULT_FORMATTER) : null;
    }

    public static String format(LocalDateTime dateTime, String pattern) {
        return dateTime != null ? dateTime.format(DateTimeFormatter.ofPattern(pattern)) : null;
    }

    public static LocalDateTime parse(String dateTimeString) {
        return dateTimeString != null ? LocalDateTime.parse(dateTimeString, DEFAULT_FORMATTER) : null;
    }

    public static LocalDateTime parse(String dateTimeString, String pattern) {
        return dateTimeString != null ? LocalDateTime.parse(dateTimeString, DateTimeFormatter.ofPattern(pattern)) : null;
    }

    public static boolean isExpired(LocalDateTime dateTime) {
        return dateTime != null && dateTime.isBefore(LocalDateTime.now());
    }

    public static LocalDateTime addMinutes(LocalDateTime dateTime, long minutes) {
        return dateTime != null ? dateTime.plusMinutes(minutes) : null;
    }

    public static LocalDateTime addHours(LocalDateTime dateTime, long hours) {
        return dateTime != null ? dateTime.plusHours(hours) : null;
    }

    public static LocalDateTime addDays(LocalDateTime dateTime, long days) {
        return dateTime != null ? dateTime.plusDays(days) : null;
    }
}
