CREATE TABLE payment_audit_log (
    id BIGSERIAL PRIMARY KEY,
    payment_id BIGINT NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_audit_payment FOREIGN KEY (payment_id) REFERENCES payments(id) ON DELETE CASCADE
);

CREATE INDEX idx_audit_payment_id ON payment_audit_log(payment_id);
CREATE INDEX idx_audit_event_type ON payment_audit_log(event_type);
