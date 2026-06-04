DROP TRIGGER IF EXISTS trigger_update_updated_at ON tf_tasks;

CREATE TRIGGER trigger_update_updated_at
    BEFORE UPDATE ON tf_tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


DROP TRIGGER IF EXISTS trigger_update_updated_at ON tf_users;

CREATE TRIGGER trigger_update_updated_at
    BEFORE UPDATE ON tf_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


DROP TRIGGER IF EXISTS trigger_update_updated_at ON tf_projects;

CREATE TRIGGER trigger_update_updated_at
    BEFORE UPDATE ON tf_projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();