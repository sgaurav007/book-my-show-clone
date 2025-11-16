-- Create notifications table
CREATE TABLE notifications (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    channel VARCHAR(20) NOT NULL,
    recipient VARCHAR(255),
    subject VARCHAR(500),
    content TEXT,
    status VARCHAR(20) NOT NULL,
    metadata TEXT,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_notification_type ON notifications(notification_type);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_notifications_user_type ON notifications(user_id, notification_type);
CREATE INDEX idx_notifications_user_status ON notifications(user_id, status);

-- Add comments to table and columns
COMMENT ON TABLE notifications IS 'Stores notification records for emails, SMS, and push notifications';
COMMENT ON COLUMN notifications.id IS 'Primary key';
COMMENT ON COLUMN notifications.user_id IS 'ID of the user receiving the notification';
COMMENT ON COLUMN notifications.notification_type IS 'Type of notification (e.g., BOOKING_CONFIRMED, PAYMENT_SUCCESS)';
COMMENT ON COLUMN notifications.channel IS 'Channel used for notification (EMAIL, SMS, PUSH)';
COMMENT ON COLUMN notifications.recipient IS 'Email address or phone number of the recipient';
COMMENT ON COLUMN notifications.subject IS 'Subject line for email notifications';
COMMENT ON COLUMN notifications.content IS 'Content/body of the notification';
COMMENT ON COLUMN notifications.status IS 'Status of notification (SUCCESS, FAILED, PENDING)';
COMMENT ON COLUMN notifications.metadata IS 'Additional metadata in JSON format';
COMMENT ON COLUMN notifications.error_message IS 'Error message if notification failed';
COMMENT ON COLUMN notifications.created_at IS 'Timestamp when notification was created';
COMMENT ON COLUMN notifications.updated_at IS 'Timestamp when notification was last updated';
